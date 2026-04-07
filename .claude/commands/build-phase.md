You are running the full BooktoAudiobook development pipeline for a new phase or feature.

The user has requested: $ARGUMENTS

Follow these steps **in sequence**. Do not skip steps or jump ahead. After each step, confirm completion before moving to the next.

---

## Step 1 — CEO Review (`/plan-ceo-review`)

Run the CEO/founder-mode plan review:
- Is this the right thing to build?
- Does it align with the product vision (indie authors, best-in-class UX, pay-per-use)?
- Is there a 10-star version of this feature?
- Should scope expand, hold, or shrink?

Present findings and get user confirmation before proceeding.

---

## Step 2 — Engineering Review (`/plan-eng-review`)

Run the engineering manager-mode plan review:
- Exact architecture and data flow
- File-by-file implementation plan
- Edge cases, error states, security considerations
- Test coverage plan
- Performance implications

Present the plan and get user confirmation before proceeding.

---

## Step 3 — Update PRD (`tasks/prd.md`)

Update `tasks/prd.md` to reflect the new phase/feature:
- Add the feature to the appropriate phase section
- Document acceptance criteria
- Note any dependencies or open decisions

Also update `tasks/todo.md` with the new sprint tasks (checkable items).

Confirm with the user that the PRD looks correct before building.

---

## Step 4 — Build (Parallel Subagents)

Spawn parallel subagents — one per module. Each subagent gets:
- A specific, scoped task (e.g., "build the Stripe webhook handler in backend/billing.py")
- The relevant files to read/modify
- Clear success criteria

Do NOT put multiple modules in one subagent. Maximize parallelism.

After all subagents complete, verify each output meets its success criteria.

---

## Step 5 — Code Review (`/review`)

Run the pre-landing code review:
- Check for SQL safety, LLM trust boundary violations, conditional side effects
- Security issues (injection, auth bypass, data leaks)
- Missing error handling at system boundaries
- Any regressions in existing functionality

Fix all issues found before proceeding.

---

## Step 6 — Ship (`/ship`)

Run the ship workflow:
- Merge main, run tests
- Bump VERSION, update CHANGELOG
- Commit, push, create PR

Report the PR URL to the user.

---

**Important:** If anything goes sideways at any step — unexpected complexity, a blocker, a design flaw — STOP and re-plan. Do not push through with a hacky fix.
