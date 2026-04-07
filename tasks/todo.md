# Tasks — Book to Audiobook

## Completed
- [x] CEO/scope review of product concept
- [x] Tech stack decision — ElevenLabs for MVP, Kokoro for v2
- [x] Pivot: desktop app → web app
- [x] Pricing model — pay-per-use + subscription (not one-time $99)
- [x] PRD written and updated (tasks/prd.md)
- [x] Stack decisions locked: FastAPI, Inngest, Clerk, Cloudflare R2
- [x] Phase 0 scaffold built (frontend/ + backend/)
- [x] CLAUDE.md updated to reflect current product

## Phase 0 — Core Pipeline (Now)
- [ ] Add ElevenLabs API key to backend/.env
- [ ] Add Cloudflare R2 credentials to backend/.env
- [ ] Install frontend deps: `cd frontend && npm install`
- [ ] Install backend deps: `cd backend && pip install -r requirements.txt`
- [ ] Run end-to-end test with a real DOCX file
- [ ] Replace placeholder voice IDs with real ElevenLabs voice IDs
- [ ] Verify MP3 output meets ACX loudness standards (−23 LUFS, 192kbps)

## Phase 1 — Auth + Billing (Week 2)
- [ ] Clerk auth (email + Google OAuth)
- [ ] Stripe pay-per-book flow
- [ ] Free trial (10K chars, no credit card)
- [ ] User dashboard (past jobs + downloads)
- [ ] 7-day file expiry + S3/R2 cleanup job
- [ ] Inngest job queue integration (replace background thread)

## Phase 2 — Polish + Beta (Week 3)
- [ ] Voice library UI (curated ElevenLabs voices + 15s preview)
- [ ] Real-time progress (WebSocket or polling)
- [ ] Chapter list UI (show detected + allow manual edit)
- [ ] Error handling + retry UI
- [ ] Beta with 5 indie authors

## Phase 3 — Launch (Week 4)
- [ ] Bug fixes from beta
- [ ] Landing page + pricing page
- [ ] Launch: Product Hunt + Reddit (r/selfpublish, r/writing)

## Open Decisions
- [ ] ElevenLabs plan tier — Creator ($22/mo, 1M chars) vs Scale ($99/mo, 10M chars)

## Backlog (Phase 1)
- [ ] Handle long chapters — split text into ~5K char blocks, generate multiple audio clips, stitch with ffmpeg

## Backlog (v2)
- [ ] Offline tier (Kokoro TTS)
- [ ] Voice cloning
- [ ] Multi-character voices
- [ ] EPUB ingestion
- [ ] Publisher dashboard
- [ ] White-label API
- [ ] Desktop app (Electron/Tauri)
