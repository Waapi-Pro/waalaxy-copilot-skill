# List cleaning

Remove false positives from a CSV of LinkedIn profiles against a locked target. A false positive is a
row that does not match the target's inclusion criteria, or that hits an exclusion criterion.

Goal: a cleaner list the user imports into Waalaxy. Precision matters more than volume. A tight list
of 1,000 to 1,500 right people beats a loose list of 5,000.

---

## Procedure

### 1. Inspect the file with code

Never assume column names. Read the CSV with pandas, print the columns and the first few rows, and
map which columns carry:

- full name / profile URL (identity, keep for output)
- current job title
- current company
- industry (often absent in scrapes)
- location
- seniority (often absent; infer from title)

Column names vary by source (Waalaxy export, Sales Nav export, third-party scrape). Map by content,
not by exact header. Handle missing columns gracefully: if industry is absent, judge on title +
company + location only, and say so in the summary.

### 2. Map columns to the target axes

The scorer maps columns by content, not by header name, and handles missing columns. Before running
it, sanity-check that the CSV carries text for at least the trade signal (title, occupation, headline,
or company). If industry and headcount columns are absent, the matrix judges on title, occupation, and
location text alone, which is normal for LinkedIn scrapes.

### 3. Score each row with the matrix

Run `scripts/score_list.py`. It applies a fixed scoring matrix. The matrix never changes. Only the
target values plug in. It works for any CSV and any target.

```
python scripts/score_list.py --csv <uploaded.csv> --target <target.json> --out <outdir>
```

Build `target.json` from the locked target card:

```json
{
  "name": "Solo tradespeople & micro-entrepreneurs",
  "location": "France",
  "job_titles": ["Owner", "Founder", "Craftsman", "Self-employed Tradesperson"],
  "industry": ["Construction", "Plumbing", "Locksmithing", "Roofing", "Glazing"],
  "company_size": "1-10",
  "exclusions": ["intern", "assistant", "student"]
}
```

Add native-language synonyms to `industry` when the CSV is not in English. A French BTP scrape needs
"electricien", "plombier", "couvreur" in the industry list, or the trade axis reads zero. Do the same
for `exclusions` (off-target trades, agency roles, marketing titles).

**The matrix (fixed weights):**

| Axis | Weight | Full points when | Partial | Zero |
|------|--------|------------------|---------|------|
| Industry / trade | 45 | direct industry-term hit in a dedicated industry/sector column | adjacent term | no hit (only when an industry column exists) |
| Role / seniority | 30 | title in target set | decision-maker term (0.85) or employee term (0.2) | exclusion title forces 0 |
| Location | 15 | location inside target region/country | — | outside target |
| Exclusion penalty | 0 to -40 | — | — | each exclusion hit subtracts 20, capped at 40 |

**Bands:** score >= 70 keep. 40 to 69 review. below 40 drop.

The industry axis only ever scores against a genuine industry/sector column (detected by header:
industry, secteur, sector, activite, domaine). Most LinkedIn scrapes don't have one — in that case
the axis is always neutral (half points), never zero. The script cannot penalize a lead for data the
CSV never collected; a missing industry column is not a mismatch.

The matrix is conservative by design. A missing field never auto-drops. It lowers the axis to neutral
so the row lands in review, not drop. A wrongly dropped lead is invisible to the user. A wrongly kept
one only costs a connection request.

The script writes `cleaned_list.csv`, `dropped.csv`, `review.csv`, `scored_full.csv`, and prints the
summary. Do not hand-classify. Run the script, read its summary, present the files.

### 4. Output

The scorer produces and you present:

- `cleaned_list.csv` — kept rows, original columns preserved plus a `score` column, ready for Waalaxy import.
- `dropped.csv` — dropped rows plus `score` and `drop_reason`.
- `review.csv` — ambiguous rows plus `score` and reason, for the user to eyeball.
- `scored_full.csv` — every row with all four axis scores, for auditing the matrix.

Present the files. Give the summary in chat: total in, kept, dropped, in review, top 3 drop reasons.
Never return only a summary. Never silently delete. Every drop is visible and reversible.

---

## Matching guidance

- Match titles on meaning, not string equality. Build a small synonym set from the target titles
  (e.g. Head of X ≈ X Lead ≈ X Manager ≈ VP of X) and match against it.
- Treat seniority as a gate when the target specifies it: a target for decision-makers should drop
  clear non-decision titles (intern, assistant, junior, student) even if the topic word matches.
- Do not over-fit to one column. A row with a strong title match and missing industry is a keep, not
  a drop.
- Respect location granularity. If the CSV has a city, roll it up to its country or major region
  before judging against the target region.

---

## Example summary

```
List cleaning — target: Head of Growth, SaaS, 51-200, DACH

In:       2,140 rows
Kept:     1,283
Dropped:    742
Review:     115

Top drop reasons:
  1. Title not a growth/decision role (411)
  2. Location outside DACH (208)
  3. Excluded title (intern/assistant/student) (123)

Files: cleaned_list.csv, dropped.csv, review.csv
```
