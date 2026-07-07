# Waalaxy Copilot

A Claude plugin: the **Waalaxy Targeting Copilot** skill plus the **Waalaxy MCP connector**, bundled
so one install sets up both.

```
/plugin marketplace add Waapi-Pro/waalaxy-copilot-skill
/plugin install waalaxy-copilot
```

The first time you use a Waalaxy tool, Claude opens a browser sign-in (magic link to your Waalaxy
account email) — same OAuth flow as the manual connector, just triggered automatically instead of
being set up by hand.

## What's in here

- [`skills/waalaxy-copilot-skill/`](./skills/waalaxy-copilot-skill) — the skill itself: `SKILL.md`
  orchestrates the flow (website → scored targets → LinkedIn/Sales Nav search URL → 3-message
  sequence → CSV list cleaning → Waalaxy import), `references/` holds the detailed method for each
  step, `scripts/score_list.py` is the deterministic scoring matrix used for list cleaning.
- [`.mcp.json`](./.mcp.json) + [`.claude-plugin/`](./.claude-plugin) — the plugin manifest and the
  bundled Waalaxy MCP server config (SSE, OAuth). This is what makes `/plugin install` set up the
  connector alongside the skill.
- [`adapters/`](./adapters) — the same workflow ported to a **Custom GPT** (ChatGPT) and a **Gemini
  Gem**, for customers who don't use Claude. See `adapters/README.md` for what's equivalent and what
  isn't (mainly: no MCP-style one-step install on either platform, and Gemini's code execution for
  list cleaning is less certain than ChatGPT's or Claude's).

## Updating the skill

`skills/waalaxy-copilot-skill/` is the single source of truth. If you change the scoring matrix, the
sequence-writing rules, or the search URL format, update it there first, then check whether
`adapters/chatgpt/INSTRUCTIONS.md` and `adapters/gemini/INSTRUCTIONS.md` (condensed paraphrases of
`SKILL.md`) still match before re-publishing the GPT/Gem.
