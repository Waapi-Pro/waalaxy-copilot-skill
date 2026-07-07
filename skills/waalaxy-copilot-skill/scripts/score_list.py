#!/usr/bin/env python3
"""
Score a CSV of LinkedIn profiles against a locked target.

Target-agnostic. The matrix (axes, weights, bands) is fixed. Every target-specific
value is passed in via a JSON target file. Works for any CSV and any target.

Matrix
------
Axis 1 - Industry/trade match     45 pts
Axis 2 - Role/seniority match     30 pts
Axis 3 - Location match           15 pts
Axis 4 - Exclusion penalty     0 to -40 pts

Bands
-----
score >= 70  -> keep
40 <= score < 70 -> review
score < 40   -> drop

Usage
-----
python score_list.py --csv leads.csv --target target.json --out ./out

target.json shape (all fields optional except job_titles + industry):
{
  "name": "Solo tradespeople & micro-entrepreneurs",
  "location": "France",
  "job_titles": ["Owner", "Founder", "Craftsman", "Self-employed Tradesperson"],
  "industry": ["Construction", "Plumbing", "Locksmithing", "Roofing", "Glazing", "Electrical Services"],
  "company_size": "1-10",
  "exclusions": ["intern", "assistant", "student"]
}
"""

import argparse
import json
import re
import sys
import unicodedata

import pandas as pd

# ----- weights (fixed, do not change per target) -----
W_INDUSTRY = 45
W_ROLE = 30
W_LOCATION = 15
EXCLUSION_CAP = 40
KEEP_BAND = 70
REVIEW_BAND = 40

# ----- seniority vocab, language-agnostic, target-independent -----
DECISION_TERMS = [
    "founder", "fondateur", "fondatrice", "fundador", "co-founder", "cofounder", "cofondateur",
    "ceo", "gerant", "gerante", "dirigeant", "dirigeante", "patron", "president", "owner",
    "proprietaire", "artisan", "artisane", "a son compte", "self-employed", "self employed",
    "independant", "independante", "freelance", "chef d entreprise", "head", "director",
    "directeur", "directrice", "managing", "associe", "partner",
]
EMPLOYEE_TERMS = [
    "intern", "stagiaire", "apprenti", "apprentice", "assistant", "assistante", "junior",
    "student", "etudiant", "trainee", "salarie", "employe", "employee", "technicien",
    "monteur", "operateur", "operator", "aide", "manoeuvre",
]

# ----- location: map of country -> tokens that imply that country -----
# extend as needed; matching is substring on the normalized location string
COUNTRY_TOKENS = {
    "france": ["france", "ile-de-france", "grand est", "occitanie", "nouvelle-aquitaine",
               "auvergne-rhone-alpes", "provence", "bretagne", "normandie", "hauts-de-france",
               "bourgogne", "pays de la loire", "centre-val", "corse", "paca"],
    "united states": ["united states", "usa", "u.s.", "california", "new york", "texas", "florida"],
    "united kingdom": ["united kingdom", "uk", "england", "scotland", "wales", "london"],
    "germany": ["germany", "deutschland", "berlin", "munich", "bavaria"],
    "spain": ["spain", "espana", "madrid", "barcelona"],
    "belgium": ["belgium", "belgique", "brussels", "bruxelles"],
    "canada": ["canada", "quebec", "ontario", "toronto", "montreal"],
}


def norm(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def any_term(haystack, terms):
    for t in terms:
        tn = norm(t)
        if tn and re.search(r"\b" + re.escape(tn), haystack):
            return True
    return False


def count_terms(haystack, terms):
    n = 0
    for t in terms:
        tn = norm(t)
        if tn and re.search(r"\b" + re.escape(tn), haystack):
            n += 1
    return n


def detect_columns(df):
    """Map columns by content, not header name. Return a dict of role -> [columns]."""
    cols = {c: norm(c) for c in df.columns}
    title_like, trade_like, loc_like, company_like, industry_like = [], [], [], [], []
    for c, cn in cols.items():
        if any(k in cn for k in ["job title", "jobtitle", "headline", "title", "position", "poste"]):
            title_like.append(c)
        if any(k in cn for k in ["occupation", "metier", "trade", "role", "fonction"]):
            trade_like.append(c)
        if any(k in cn for k in ["location", "region", "city", "ville", "country", "pays", "state", "area"]):
            loc_like.append(c)
        if any(k in cn for k in ["company", "entreprise", "societe", "organisation", "organization"]):
            company_like.append(c)
        if any(k in cn for k in ["industry", "secteur", "sector", "activite", "domaine"]):
            industry_like.append(c)
    # signal text = everything that can carry trade or title info
    signal_cols = list(dict.fromkeys(title_like + trade_like + company_like))
    return {
        "signal": signal_cols if signal_cols else list(df.columns),
        "title": list(dict.fromkeys(title_like + trade_like)),
        "location": loc_like,
        "industry": industry_like,
    }


def row_text(row, cols):
    parts = [str(row[c]) for c in cols if c in row and pd.notna(row[c])]
    return norm(" ".join(parts))


def score_industry(sig_text, industries, has_industry_col):
    """45 pts. Full on a direct industry-term hit, partial on a single weak hit, 0 on none.

    Neutral whenever the axis can't be judged: no industry values in the target, or no
    industry-like column in the CSV. LinkedIn scrapes routinely lack an industry column,
    and zeroing the axis in that case would drop otherwise-good leads on missing data
    rather than a real mismatch.
    """
    if not industries or not has_industry_col:
        reason = "no industry in target, neutral" if not industries else "no industry column in csv, neutral"
        return W_INDUSTRY * 0.5, reason
    hits = count_terms(sig_text, industries)
    # also try each industry split into words for partial matches
    word_terms = []
    for ind in industries:
        word_terms += [w for w in norm(ind).split() if len(w) > 3]
    word_hits = count_terms(sig_text, word_terms)
    if hits >= 1:
        return W_INDUSTRY, f"industry match ({hits})"
    if word_hits >= 1:
        return W_INDUSTRY * 0.55, "adjacent industry term"
    return 0, "no industry signal"


def score_role(title_text, sig_text, job_titles, exclusions):
    """30 pts. Exclusion title forces 0. Decision title full. Employee title low."""
    hay = title_text if title_text else sig_text
    if exclusions and any_term(hay, exclusions):
        return 0, "role hits target exclusion"
    if job_titles and any_term(hay, job_titles):
        return W_ROLE, "title in target set"
    if any_term(hay, DECISION_TERMS):
        return W_ROLE * 0.85, "decision-maker seniority"
    if any_term(hay, EMPLOYEE_TERMS):
        return W_ROLE * 0.2, "employee-level seniority"
    return W_ROLE * 0.5, "seniority unclear"


def score_location(loc_text, target_location):
    """15 pts. In-region full, out-of-region 0, missing neutral half."""
    if not target_location:
        return W_LOCATION * 0.5, "no target location"
    if not loc_text:
        return W_LOCATION * 0.5, "no location data"
    tl = norm(target_location)
    if tl in loc_text:
        return W_LOCATION, "location in target"
    # roll up via country tokens
    for country, tokens in COUNTRY_TOKENS.items():
        if tl == country or tl in tokens:
            if any(tok in loc_text for tok in tokens):
                return W_LOCATION, "location in target country"
    return 0, "location outside target"


def score_exclusions(sig_text, exclusions):
    """0 to -40. Each distinct exclusion hit subtracts, capped."""
    if not exclusions:
        return 0, ""
    hits = count_terms(sig_text, exclusions)
    if hits == 0:
        return 0, ""
    pen = min(EXCLUSION_CAP, hits * 20)
    return -pen, f"exclusion hits ({hits})"


def band(score):
    if score >= KEEP_BAND:
        return "keep"
    if score >= REVIEW_BAND:
        return "review"
    return "drop"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", default="./out")
    args = ap.parse_args()

    with open(args.target) as f:
        target = json.load(f)

    df = pd.read_csv(args.csv)
    cols = detect_columns(df)

    industries = target.get("industry", [])
    job_titles = target.get("job_titles", [])
    exclusions = target.get("exclusions", [])
    location = target.get("location", "")
    has_industry_col = bool(cols["industry"])

    rows = []
    for _, r in df.iterrows():
        sig = row_text(r, cols["signal"])
        title = row_text(r, cols["title"])
        loc = row_text(r, cols["location"])
        ind_text = row_text(r, cols["industry"]) if has_industry_col else ""

        s_ind, r_ind = score_industry(ind_text, industries, has_industry_col)
        s_role, r_role = score_role(title, sig, job_titles, exclusions)
        s_loc, r_loc = score_location(loc, location)
        s_exc, r_exc = score_exclusions(sig, exclusions)

        total = round(max(0, s_ind + s_role + s_loc + s_exc))
        reasons = [x for x in [r_ind, r_role, r_loc, r_exc] if x]
        rows.append({
            "score": total,
            "verdict": band(total),
            "score_industry": round(s_ind),
            "score_role": round(s_role),
            "score_location": round(s_loc),
            "score_exclusion": round(s_exc),
            "score_reason": " | ".join(reasons),
        })

    scored = pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)

    import os
    os.makedirs(args.out, exist_ok=True)
    kept = scored[scored.verdict == "keep"]
    dropped = scored[scored.verdict == "drop"]
    review = scored[scored.verdict == "review"]

    orig_cols = list(df.columns)
    kept[orig_cols + ["score"]].to_csv(f"{args.out}/cleaned_list.csv", index=False)
    dropped[orig_cols + ["score", "score_reason"]].rename(
        columns={"score_reason": "drop_reason"}).to_csv(f"{args.out}/dropped.csv", index=False)
    review[orig_cols + ["score", "score_reason"]].to_csv(f"{args.out}/review.csv", index=False)
    scored.to_csv(f"{args.out}/scored_full.csv", index=False)

    # summary
    top_drop = (dropped["score_reason"].str.split(" \\| ").explode()
                .value_counts().head(3)) if len(dropped) else pd.Series(dtype=int)
    print(f"List scoring - target: {target.get('name','(unnamed)')}")
    print(f"In:      {len(scored)}")
    print(f"Kept:    {len(kept)}")
    print(f"Dropped: {len(dropped)}")
    print(f"Review:  {len(review)}")
    print("Top drop reasons:")
    for reason, n in top_drop.items():
        print(f"  {reason} ({n})")
    print(f"Columns mapped -> signal:{cols['signal']} | title:{cols['title']} | location:{cols['location']} "
          f"| industry:{cols['industry']}")
    if not has_industry_col:
        print("No industry column detected in the CSV - industry axis scored neutral for every row.")


if __name__ == "__main__":
    main()
