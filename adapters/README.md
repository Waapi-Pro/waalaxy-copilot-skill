# Adapters: same copilot on ChatGPT and Gemini

This skill was built for Claude Code. These two folders each port it to one non-Claude platform, so
a Waalaxy customer without Claude can get the same targeting → search URL → sequence → list-clean
flow:

| Platform | Folder | What you build there |
|---|---|---|
| ChatGPT | [`chatgpt/`](./chatgpt) | A **Custom GPT** — [`README.md`](./chatgpt/README.md) is the build guide, [`INSTRUCTIONS.md`](./chatgpt/INSTRUCTIONS.md) is what you paste into the GPT's Instructions field. |
| Gemini | [`gemini/`](./gemini) | A **Gem** — [`README.md`](./gemini/README.md) is the build guide, [`INSTRUCTIONS.md`](./gemini/INSTRUCTIONS.md) is what you paste into the Gem's Instructions field. |

Each folder is self-contained: open its `README.md`, follow the steps, paste its `INSTRUCTIONS.md`
where told. You do not need the other folder to build either one.

Both reuse the same source of truth as the Claude skill: `../references/*.md` and
`../scripts/score_list.py`. Update those files first when the underlying logic changes (matrix
weights, sequence rules, search URL format), then re-check whether the condensed `INSTRUCTIONS.md`
in each adapter still matches before re-publishing the GPT/Gem — the instructions are a compressed
paraphrase of the reference files, not a separate spec.

## Why two extra files per platform instead of one shared prompt

GPT Builder and the Gemini Gem builder both cap the "Instructions" field size (roughly 8k characters
on the GPT side), which is smaller than the combined reference docs (~50k characters). So each
platform gets a short **orchestrator** prompt (mirrors `SKILL.md`'s step flow) plus the same
reference docs attached as **knowledge files** the model opens on demand — same pattern Claude uses
between `SKILL.md` and `references/`.

## Known gaps vs. the Claude version

- **CSV cleaning (Step 5)** needs deterministic script execution, not eyeballing. ChatGPT's Code
  Interpreter covers this reliably. Gemini's code execution support inside a Gem is less certain —
  test it before trusting it on a real client list (see `gemini/README.md`).
- **Waalaxy MCP import (Step 6/7 in the Claude version)** works in Claude and ChatGPT (both support
  MCP connectors — see `../references/waalaxy-mcp.md`). Gemini Gems have no equivalent today; the
  Gemini adapter always hands back a file or link for manual import instead.
- **Persistent `prospecting-strategy.md`**: Claude writes and updates a real file across the session.
  Neither GPT nor Gem instructions can guarantee a live file the same way — both are told to reprint
  the running recap in chat, and to also produce a downloadable file if Code Interpreter is on.

None of these gaps break the core flow (targets → search URL → sequence). They only affect the two
features that lean on side effects (running code deterministically, writing files, pushing to
Waalaxy) rather than pure text generation.
