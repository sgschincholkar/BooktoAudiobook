# Book to Audiobook — Project Context

## Product
Web app that converts books/documents into professional audiobooks using ElevenLabs TTS (cloud, MVP) with Kokoro offline TTS planned for v2.
- **Pricing:** Pay-per-use (~$5–15/book) + subscription ($29/mo Pro, $99/mo Publisher)
- **Free trial:** First 10,000 characters free, no credit card
- **Core differentiator:** Best-in-class voice quality (ElevenLabs), simple UX, no setup
- **Target:** Indie authors, small publishers, accessibility-focused orgs
- **vs. alternatives:** $5,000+ voice actors, complex cloud tools with poor UX

## Current State
- PRD written: `tasks/prd.md`
- Phase 0 scaffold built: `frontend/` (Next.js) + `backend/` (FastAPI)
- Next step: Add API keys and run end-to-end pipeline

## Tech Stack (Locked)
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | FastAPI (Python) |
| Auth | Clerk |
| DOCX parsing | mammoth (Python) |
| PDF parsing | pdfplumber (Python) |
| TTS (MVP) | ElevenLabs API |
| TTS (v2) | Kokoro 82M (offline) |
| Audio | ffmpeg (WAV → MP3, loudness norm) |
| Job queue | Inngest |
| Storage | Cloudflare R2 |
| Database | PostgreSQL (Supabase) |
| Payments | Stripe |
| Hosting | Vercel (frontend) + Railway/Fly.io (backend) |

## Project Structure
```
newBooktoAudiobook/
├── frontend/          # Next.js 14 app
├── backend/           # FastAPI (Python)
├── .env.example       # All required env vars
├── README.md
├── CLAUDE.md          # This file
└── tasks/
    ├── prd.md         # Full product requirements
    ├── todo.md        # Sprint tasks
    └── lessons.md     # Corrections & learnings
```

## gstack Workflow (Follow This Sequence)
Every feature or decision must go through this pipeline:

1. **Brainstorm** → `/plan-ceo-review` — is this the right thing to build?
2. **Architecture** → `/plan-eng-review` — how exactly do we build it?
3. **PRD** → update `tasks/prd.md` before any code
4. **Build** → spawn parallel subagents per module (one task per subagent)
5. **Review** → `/review` — catch production bugs before merge
6. **Ship** → `/ship`

## Session Start Checklist
1. Read `tasks/lessons.md` to recall past corrections
2. Read `tasks/todo.md` to resume where we left off
3. Read this file to confirm current product state
4. Confirm current goal with user before proceeding

## IMPORTANT: Keep This File Updated
- Update **Product**, **Current State**, and **Tech Stack** whenever pivots happen
- This file is the single source of truth for what the product is today

## Value Ladder
- Lead Magnet: Free trial (10K chars, no card)
- Core: Pay-per-book (~$5–15/book)
- Continuity: Pro — $29/month (3 books/mo)
- Growth: Publisher — $99/month (10 books/mo)
- Add-ons: Premium voice packs (post-MVP)
- Backend: Partnership/white-label licensing (post-MVP)

## v2 Roadmap
- Offline tier: Kokoro TTS (local processing, privacy-first)
- Voice cloning
- Multi-character voices
- EPUB support
- Desktop app (Electron/Tauri)
