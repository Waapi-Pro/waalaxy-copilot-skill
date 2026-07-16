# Version check — is this skill up to date?

Run a lightweight freshness check **at most once every 7 days**, the first time the skill is used in
a session. It never blocks the user's task: check, maybe surface a one-line notice, then continue.

---

## CONFIG (edit these when the repo changes)

- **Local version file:** `VERSION` at the skill root (source of truth, one line, semver).
- **Repo:** `https://github.com/Waapi-Pro/waalaxy-copilot` (skill lives at `skills/waalaxy-copilot-skill/`).
- **Remote version URL (raw):**
  `https://raw.githubusercontent.com/Waapi-Pro/waalaxy-copilot/main/skills/waalaxy-copilot-skill/VERSION`
- **Changelog URL (raw):**
  `https://raw.githubusercontent.com/Waapi-Pro/waalaxy-copilot/main/skills/waalaxy-copilot-skill/CHANGELOG.md`
- **Update instructions shown to the user:** re-pull the skill repo — `git pull` in the cloned
  `waalaxy-copilot` directory (or re-install it from GitHub).
- **State file (writable, per machine):** `~/.waalaxy-ai-copilot-state.json`

> Confirm the remote URL points at wherever this skill is actually published before relying on it.
> If it 404s, the skill isn't in that repo/path — fix the CONFIG, don't silently skip forever.

---

## Procedure

**1. Throttle — has it been ≥7 days?**
Read the state file. It looks like:

```json
{ "last_checked": "2026-07-15", "last_seen_remote": "1.0.0" }
```

- If the file is missing, or `last_checked` is more than 7 days before today, proceed to step 2.
- Otherwise **skip the check entirely** and go straight to the user's task. Say nothing.

(Use today's date from context / `date +%F`. No network call when throttled.)

**2. Read the local version**
`cat VERSION` at the skill root → e.g. `1.0.0`.

**3. Fetch the remote version**
Fetch the raw remote URL (WebFetch, or `curl -fsSL <url>` via Bash). Timeout fast.
- On any failure (offline, 404, timeout): do **not** bother the user. Still update `last_checked` to
  today so a flaky network doesn't retry every message, and continue the task.

**4. Compare (semver)**
Parse both as `MAJOR.MINOR.PATCH` and compare numerically (not string compare — `0.10.0` > `0.9.0`).
- **Remote ≤ local:** up to date. Say nothing (or one line only if the user explicitly asked to check).
- **Remote > local:** surface the notice in step 5.

**5. Propose the update (one line, non-blocking)**
Prepend a single line to your response, then do the task the user actually asked for:

> 🔄 A newer version of the Waalaxy Copilot is available (**v{remote}**, you're on **v{local}**).
> Update with `git pull` in your `waalaxy-copilot` directory. Want the changelog?

Never re-run the skill, block, or nag more than once per session.

**6. Write state**
Write the state file with `last_checked` = today and `last_seen_remote` = the remote version you saw
(or the local one if the fetch failed). This is what enforces "once a week".

---

## On-demand check

If the user explicitly asks "is the copilot up to date?" / "check for updates", run steps 2–5
**ignoring the 7-day throttle**, and always answer (including "✅ You're on the latest, v{local}.").
Still update the state file afterward.

---

## Versioning rule (for maintainers pushing to the repo)

Bump `VERSION` on every push that changes skill behavior, using semver:

- **PATCH** (`1.0.0 → 1.0.1`) — copy tweaks, typo fixes, clarifications, no behavior change.
- **MINOR** (`1.0.1 → 1.1.0`) — new capability or reference file, backward-compatible (e.g. adding a
  new module).
- **MAJOR** (`1.1.0 → 2.0.0`) — restructure that changes how existing steps behave or breaks a flow.

Keep a short `CHANGELOG.md` at the skill root, newest first, so the "Want the changelog?" prompt has
something to show:

```
## 1.1.0 — 2026-07-15
- Added Website Analyzer and Profile Optimization modules.
- Website Analyzer can emit an AI-builder rebuild prompt.
```
