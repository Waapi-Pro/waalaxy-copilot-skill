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

### 2. Judge each row against the target

For each row, compare to the locked target:

- **Title match** — does the current title fit the target's job titles, allowing for synonyms and
  seniority variants? "Growth Manager" fits a "Head of Growth" target; "Marketing Intern" does not.
- **Industry match** — if industry is present and the target specifies industries, does it fit? If
  absent, skip this check rather than dropping on missing data.
- **Company size** — if the data carries headcount, check the band. If absent, skip.
- **Location** — does it fall inside the target region at country / major-region level? Respect the
  granularity rule.
- **Exclusions** — drop if the row hits an exclusion title, industry, company size, or company type
  from the target.

### 3. Classify, do not delete

Mark every row as one of:

- **keep** — clearly fits inclusion, no exclusion hit.
- **drop** — clearly fails inclusion or hits an exclusion. Record a one-line reason.
- **review** — genuinely ambiguous (e.g. vague title like "Consultant", missing key fields). When a
  row could plausibly fit, mark review, not drop.

Be conservative on drops. A wrongly dropped lead is invisible to the user; a wrongly kept one only
costs them a connection request. When unsure, lean keep or review.

### 4. Output

Produce and present:

- `cleaned_list.csv` — kept rows, original columns preserved, ready for Waalaxy import.
- `dropped.csv` — dropped rows plus a `drop_reason` column.
- `review.csv` — ambiguous rows, if any, for the user to eyeball.
- A short summary in chat: total rows in, kept, dropped, in review, and the top 3 drop reasons.

Save files to the outputs directory and present them. Never return only a summary; the user needs the
actual files. Never silently delete; every drop must be visible and reversible.

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
