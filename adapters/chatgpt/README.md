# Build the "Waalaxy Targeting Copilot" Custom GPT

Go to chatgpt.com → **Explore GPTs** → **Create** → switch to the **Configure** tab (skip the chat
builder, fill the fields directly).

## 1. Name
`Waalaxy Targeting Copilot`

## 2. Description
`From a website to a clean LinkedIn list and a ready-to-send outreach sequence — targets, search URL, messages, and CSV cleaning for Waalaxy.`

## 3. Instructions
Paste the full contents of [`INSTRUCTIONS.md`](./INSTRUCTIONS.md) (same folder) into the
**Instructions** field.

## 4. Conversation starters
- `Analyze my website and suggest targets`
- `Build me a LinkedIn search URL for my target`
- `Write my 3-message outreach sequence`
- `Clean this lead list`

## 5. Knowledge — upload these files
From `../../skills/waalaxy-copilot-skill/references/` and `../../skills/waalaxy-copilot-skill/scripts/`:
- `target-prompts.md`
- `search-url-builder.md`
- `sequence-writer.md`
- `list-cleaning.md`
- `prospecting-strategy-template.md`
- `score_list.py`

Upload all six under **Knowledge**. `score_list.py` is a `.py` file — GPT accepts it as a knowledge
upload; the instructions tell the model to execute it with Code Interpreter rather than read it as
prose.

## 6. Capabilities
Enable:
- ✅ **Web Browsing** — required for Step 1 (reading the target's website).
- ✅ **Code Interpreter & Data Analysis** — required for Step 5 (running `score_list.py` against an
  uploaded CSV, and for reading `score_list.py` from Knowledge). If your GPT Builder version has a
  separate toggle for "file accessible to Code Interpreter" per uploaded file, turn it on for
  `score_list.py` specifically — otherwise Code Interpreter may not be able to `import` or run it and
  the model should instead copy the script into a fresh Python file before executing it.
- ❌ DALL·E image generation — not needed, leave off (optional, harmless either way).
- ❌ Actions — none required for the core flow. See the note on the Waalaxy connector below.

## 7. Model
Pick the best-reasoning model available in GPT Builder (GPT-5-class). This copilot leans on strict
multi-constraint writing (`sequence-writer.md`) and a fixed scoring matrix — weaker models drift from
the rules over a long conversation.

## 8. The Waalaxy import connector (Step 6) — separate from this GPT

The Waalaxy → Waalaxy MCP connector is a per-account "App"/connector in ChatGPT, not a setting inside
this GPT's configuration. The user (or you, testing) enables it once via:

**Settings → Apps → Advanced Settings → enable Developer Mode → Create app**, paste
`https://stargate.prod.aws.waalaxy.com/api/mcp`, name it Waalaxy, sign in with the Waalaxy account
email.

Once connected, the Waalaxy tools are available in any chat with this GPT — including this one — and
the instructions already tell the model to offer the import only when that connector's tools are
present, and only after an explicit yes. If the connector isn't enabled, the GPT just hands back the
cleaned CSV / import link for the user to use manually, same as the base flow.

## 9. Test before sharing

Run all five steps once end to end: paste a real client's website URL, lock a target, generate the
LinkedIn URL, generate the sequence, then upload a small CSV of leads and confirm `score_list.py`
actually ran (check for `cleaned_list.csv` / `dropped.csv` / `review.csv` / `scored_full.csv` in the
response) rather than the model hand-classifying the rows itself.
