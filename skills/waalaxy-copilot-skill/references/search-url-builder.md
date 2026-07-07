# Search URL builder

Turn a locked target into a LinkedIn search, then import into Waalaxy.

---

## Default flow

1. Always generate the standard LinkedIn URL first.
2. Explain in 2-3 lines why Sales Nav would add useful extra filters for this specific target (only if true).
3. Ask whether the user has Sales Nav.
4. Depending on the answer: produce the Sales Nav payload, or present the partner.

---

## Step 1 — Standard LinkedIn URL (always)

Base: `https://www.linkedin.com/search/results/people/`

Parameters:
- `keywords` — titles in Boolean: `("Gérant" OR "Directeur Général") NOT stagiaire`
- `geoUrn` — country geo ID, encoded as `%5B%22105015875%22%5D`
- `origin` — always `FACETED_SEARCH`

### Country geoUrn table (Captain Data)

| Country | geoUrn |
|---|---|
| France | 105015875 |
| Belgium | 100565514 |
| Spain | 105646813 |
| England | 102299470 |
| Germany | 101282230 |
| Italy | 103350119 |
| United States | 103644278 |
| Canada | 101174742 |
| Australia | 101452733 |
| India | 102713980 |
| China | 102890883 |
| Japan | 101355337 |
| Brazil | 106057199 |
| Mexico | 103323778 |
| Netherlands | 102890719 |
| Singapore | 102454443 |
| Switzerland | 106693272 |
| Sweden | 105117694 |
| South Korea | 105149562 |
| Russia | 101728296 |
| United Arab Emirates | 104305776 |

To combine several countries: `geoUrn=%5B%22105015875%22%2C%22100565514%22%5D`

Regions and industries: IDs are not public, go through the LinkedIn UI.

### Construction

1. Titles in `keywords` in Boolean, URL-encoded.
2. Country geoUrn from the table if the target is at country level.
3. For industry and region: partial URL + warning + action checklist.

### Output format

**URL:**
```
[url]
```

If filters are missing (industry, region):

> ⚠️ This URL is incomplete. Without the steps below, you will get off-target results.

- [ ] Open the URL in LinkedIn
- [ ] Click **Industry** → select [exact value]
- [ ] Click **Locations** → select [exact value] *(if region)*
- [ ] Copy the final URL from the address bar
- [ ] Import it into Waalaxy via the LinkedIn import

---

## Step 2 — Transition to Sales Nav (contextual)

After the standard URL, judge whether Sales Nav would add meaningful precision for this target.

**Mention Sales Nav only when at least one of these applies:**
- Company size is a key target criterion (e.g. engineering firms 1-50, SaaS 51-200)
- Seniority must be filtered precisely (e.g. exclude juniors on a decision-maker target)
- The target is broad and would generate more than 2,500 results on standard LinkedIn

**If Sales Nav is relevant**, explain in 2-3 lines max the extra filters useful for this specific target. No generic list. Example:

> "With Sales Navigator, you could filter directly on company size (1-50 employees) and seniority (Owner, Director), which avoids importing managers from large groups or assistants. On this target, that would cut the noise significantly."

Then ask: **"Do you have access to Sales Navigator?"**

---

## Step 3 — Depending on the answer

### The user has Sales Nav → produce the payload

Do not build a Sales Nav URL by hand. Produce a structured filter payload the user applies in the UI.

**Payload generation method:**

As a B2B strategist, translate the target into Sales Navigator filters. Use only the filters the target justifies. Quality > quantity.

CORE FILTERS (always fill when the matching ICP field is present):
- `current_title.include` — 4 to 6 real LinkedIn titles
- `current_title.exclude` — 2 to 4 adjacent-but-wrong titles
- `seniority_level` — strict values: Owner, Partner, CXO, VP, Director, Manager, Senior, Entry, In Training
- `geography` — country or major region recognized by Sales Nav; never city or department
- `industry` — LinkedIn industry tags verbatim
- `company_headcount` — strict bands: Self-employed, 1-10, 11-50, 51-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+

EXPLORATORY FILTERS (add only if the target justifies it):
- `function` — strict values: Accounting, Administrative, Arts and Design, Business Development, Community and Social Services, Consulting, Education, Engineering, Entrepreneurship, Finance, Healthcare Services, Human Resources, Information Technology, Legal, Marketing, Media and Communications, Military and Protective Services, Operations, Product Management, Program and Project Management, Purchasing, Quality Assurance, Real Estate, Research, Sales, Support
- `years_in_current_position` — 0-25; useful if the pain implies tenure in the role
- `company_type` — strict values: Public Company, Privately Held, Nonprofit, Educational Institution, Partnership, Self-Employed, Self-Owned, Government Agency
- `profile_language` — "French", "English", etc.

Rules:
- Titles: real LinkedIn strings, never job families
- "Head of X" → seniority Director (Sales Nav has no "Head" enum)
- Every exploratory filter must be justifiable by the target
- Exclusions are added only if the target explicitly justifies them

**Payload output format:**

Included titles: [list]
Excluded titles: [list]
Seniority: [list]
Location: [list]
Industry: [list]
Company size: [list]
Function: [value] *(if justified)*
Tenure in role: [X-Y years] *(if justified)*
Company type: [value] *(if justified)*

**Actions:**
- [ ] Open Sales Navigator → People search
- [ ] Apply each filter above
- [ ] Check the result count: aim for 1,000 to 1,500
- [ ] If too broad: tighten on company size or seniority
- [ ] If too narrow: widen the titles or add an adjacent industry
- [ ] Save the search in Sales Nav (Waalaxy auto-syncs every 12h)
- [ ] Import into Waalaxy via the Sales Navigator import

---

### The user does not have Sales Nav → present the partner

> "Sales Navigator costs around 100€/month direct. Waalaxy has a partnership with **SalesNavSplit** that gives access at -60% by sharing a license with other users. It is the option most used by Waalaxy customers who want Sales Nav without the full price.
>
> 👉 [salesnavsplit.com/waalaxy-partnership](https://salesnavsplit.com/waalaxy-partnership)"

Do not push. Offer once, move on.

---

## After delivering the URL or payload

One line: estimated volume and the filter doing the heavy lifting.
One line: reminder of 1,000-1,500 profiles max for an effective Waalaxy campaign.
Update `prospecting-strategy.md` with the LinkedIn search section.

---

## Step 4 — Waalaxy import link (pre-filled)

Once the final LinkedIn URL is ready, generate a link that opens the Waalaxy app with the import panel
already filled. The user picks their list and clicks "Import". Nothing launches on its own.

Scope of this skill: LinkedIn searches only.
- Standard LinkedIn search → `importType=regular` (max 1000)
- Sales Navigator search → `importType=salesnav` (max 2500)

### Format

Base: `https://app.waalaxy.com/?`

Three query params:
- `importType` (required) — `regular` or `salesnav`
- `importUrl` (required) — the LinkedIn URL, **URL-encoded** (see below)
- `quantity` (optional) — number of prospects. If > max, capped to max automatically.

### Critical rule: encode importUrl

The LinkedIn URL contains `: / ? & =` which break the link if pasted as-is. URL-encode the entire
LinkedIn URL before placing it in `importUrl`:

| Character | Encoded |
|---|---|
| `:` | `%3A` |
| `/` | `%2F` |
| `?` | `%3F` |
| `&` | `%26` |
| `=` | `%3D` |
| space | `%20` |

Equivalent to `encodeURIComponent(url)` in JS. Encode the whole LinkedIn URL, params included.

### Example

LinkedIn URL:
```
https://www.linkedin.com/search/results/people/?keywords=ceo
```

Import link (import 500 profiles):
```
https://app.waalaxy.com/?importType=regular&importUrl=https%3A%2F%2Fwww.linkedin.com%2Fsearch%2Fresults%2Fpeople%2F%3Fkeywords%3Dceo&quantity=500
```

### Output format

**Waalaxy import link:**
```
[full link]
```

One line: this link pre-fills the import (type + URL + quantity). The user keeps control over the
list choice and clicks "Import".

Update `prospecting-strategy.md` with the import link.
