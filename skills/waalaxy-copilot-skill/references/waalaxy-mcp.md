# Waalaxy MCP connector

The Waalaxy AI connector links a customer's Waalaxy account to their AI assistant over MCP. Once
active, the assistant can list prospect lists and campaigns, import LinkedIn prospects, and add them
to a campaign. Every action runs with the user's own account permissions. The assistant cannot do
anything the user could not do in the Waalaxy app.

This is the fast path from a cleaned CSV to a live Waalaxy list. Offer it right after Step 5.

---

## When to offer it

- Only after a CSV has been cleaned and `cleaned_list.csv` exists.
- Never for target cards, search URLs, or sequences. Those are not imports.
- Offer once. If the user declines, stop and let them import the CSV by hand.

---

## Two paths

### Path A — connector already active

The Waalaxy tools are already in the tool list. Offer to import the kept rows.

Importing prospects is a side-effectful action. Before importing:

1. State the count of kept rows.
2. Name the destination prospect list.
3. Name the campaign, if the user wants leads dropped straight into a sequence.
4. Wait for a clear yes. Never import silently.

You can first list the user's existing lists and campaigns so they pick a real destination rather
than a guessed name. Then import, then confirm what landed. Imports appear in each prospect's history
in Waalaxy with MCP as the import source.

### Path B — connector not active

Offer the one-time setup. Keep it short. Give the URL and the connect steps. Do not paste the whole
article unless asked.

**MCP server URL:** `https://stargate.prod.aws.waalaxy.com/api/mcp`

**Connect in Claude:**
1. Customize → Connectors → Add Connectors → Add custom connectors.
2. Name it Waalaxy, paste the URL above, click Add.
3. Select Waalaxy, click Connect, then Authorize connection.
4. Open the magic link sent to the account email to finish sign-in.
5. The Waalaxy tools then appear in every new conversation.

**Connect in ChatGPT:** Settings → Apps → Advanced Settings → enable Developer Mode → Create app,
paste the same URL, name it, sign in with the Waalaxy account email.

---

## Requirements to state up front

- Waalaxy plan: Advanced or Business. If the plan is downgraded later, imports are blocked but listing
  lists and campaigns still works.
- Assistant plan: Claude Pro, Max, Team, or Enterprise, or a ChatGPT plan that supports MCP connectors.
- Sign-in uses the email linked to the Waalaxy account. Same email, every time.

---

## Limits and rules

- Browser-based sign-in only. The connector does not take Waalaxy REST API keys. For headless
  automation with no human in the loop, point the user to the Waalaxy REST API instead.
- Access tokens refresh automatically. The user will occasionally be asked to sign in again.
- Imports follow the same quotas and de-duplication rules as the rest of the Waalaxy app.

---

## Troubleshooting to relay if it fails

- Tools missing: reload the client, verify the URL is exactly the one above.
- Lists or campaigns not found: confirm sign-in used the Waalaxy account email. Ask the assistant to
  run "Test my Waalaxy connection." If it fails, disconnect and reconnect.
- Sign-in window closed early: re-trigger from the connectors panel, allow pop-ups, open the magic
  link on the same device.
