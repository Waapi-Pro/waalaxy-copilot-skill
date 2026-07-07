# Build the "Waalaxy Targeting Copilot" Gem

Go to gemini.google.com → left sidebar **Gems** → **New Gem**.

## 1. Name
`Waalaxy Targeting Copilot`

## 2. Instructions
Paste the full contents of [`INSTRUCTIONS.md`](./INSTRUCTIONS.md) (same folder) into the
**Instructions** field.

## 3. Knowledge — add these files
Use **Add knowledge files** (upload, or "Add from Drive" if you keep a copy there). From
`../../references/` and `../../scripts/`:
- `target-prompts.md`
- `search-url-builder.md`
- `sequence-writer.md`
- `list-cleaning.md`
- `prospecting-strategy-template.md`
- `score_list.py`

If the Gem UI you're on rejects `.py` uploads as knowledge, rename it to `score_list.py.txt` before
upload — the instructions still tell the model what it is and how to use it (as a script to run via
code execution, or as the exact algorithm to reproduce manually if no code tool is available).

## 4. Model
Pick Gemini's top reasoning tier available for Gems (currently the Pro-class model). The sequence
writer reference is long and constraint-heavy; a lighter/faster model will drift from the rules over
a multi-turn conversation.

## 5. Tool parity notes vs. the Claude version

Gems don't expose every capability the same way a full Gemini conversation or Claude does. Two gaps
to know about before you rely on this Gem for real client work:

- **Code execution for Step 5 (CSV cleaning) is not guaranteed.** If your Gem instance can run Python
  against an uploaded CSV, it should use `score_list.py` exactly as written — deterministic, no
  hand-classification. If it can't, the instructions tell the model to fall back to manually applying
  the same fixed matrix from `list-cleaning.md`, but that fallback is slower and more error-prone on
  large files than an actual script run. Test with a real CSV before trusting the output on a client
  list, and prefer the ChatGPT or Claude version for large lists if this Gem can't execute code.
- **No Waalaxy MCP connector.** Gemini Gems have no equivalent of Claude's or ChatGPT's Waalaxy
  connector today. This Gem always hands back a cleaned CSV or an import link for the user to import
  by hand in the Waalaxy app — it never claims to push leads into Waalaxy itself.

## 6. Test before sharing

Run all four steps once end to end: paste a real client's website URL, lock a target, generate the
LinkedIn URL, generate the sequence, then upload a small CSV of leads and check whether the cleaning
step actually executed `score_list.py` (ask it directly: "did you run the script or judge this by
eye?") before trusting it on real client lists.
