# Lessons — Book to Audiobook

## How to Use This File
After any correction from the user, add an entry here with:
- What went wrong
- The rule to follow going forward
- How to apply it

## Lessons

### 1. Keep CLAUDE.md updated on every product pivot
**What went wrong:** CLAUDE.md still described the old product (offline desktop app, $99 one-time, Electron/Kokoro) after we had pivoted to a web app with ElevenLabs and pay-per-use pricing.

**Rule:** Whenever the product changes (pricing, stack, architecture, scope), update CLAUDE.md immediately — not at the end of the session.

**How to apply:** After any pivot decision is made and confirmed by the user, update the Product, Tech Stack, and Current State sections of CLAUDE.md before moving on.

### 2. Confirm previous session context before acting
**What went wrong:** At session start, tried to act without knowing what changed in the previous session. Had to ask the user to paste the prior conversation.

**Rule:** Always read `tasks/lessons.md`, `tasks/todo.md`, and `CLAUDE.md` at session start before doing anything. If context is unclear, ask the user what changed since last time.

**How to apply:** Follow the Session Start Checklist in CLAUDE.md at the top of every session.
