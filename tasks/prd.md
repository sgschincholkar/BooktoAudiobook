# Product Requirements Document
# Book to Audiobook — MVP v1.0

**Status:** Active  
**Last Updated:** 2026-04-07  
**Scope:** Web app MVP using ElevenLabs TTS (offline Kokoro in v2)

---

## 1. Problem Statement

Indie authors want audiobook versions of their books but face two bad options:
1. Hire a voice actor → $5,000–$15,000, 6–12 week wait, must share unpublished manuscript
2. Existing cloud TTS tools → Mediocre quality, complex UX, not built for long-form books

**The gap:** No simple, affordable, high-quality audiobook creation tool exists for indie authors that just works — upload your book, pick a voice, get professional MP3s back.

---

## 2. Product Vision

A web app that turns any book into a professional audiobook in hours, not weeks.

**One-sentence pitch:**
> "Upload your Word doc or PDF, pick a voice, hit Generate — get a complete audiobook MP3 ready for ACX upload. Pay only for what you use."

---

## 3. Target User

**Primary:** Indie authors
- Self-published on Amazon KDP, Draft2Digital, Smashwords
- Knows audiobooks are valuable but can't afford $5K+ production
- Not technical — must work without any setup

**Secondary (post-MVP):** Small publishers, accessibility orgs, content creators

---

## 4. Pricing Model

Pay-as-you-go based on ElevenLabs API cost + markup:

| Tier | Price | Notes |
|------|-------|-------|
| Free Trial | First 10,000 characters free | ~3–4 pages, lets user hear quality |
| Pay-per-book | ~$5–15/book (80K words) | Based on ElevenLabs cost + 3–5x markup |
| Pro Subscription | $29/month | 3 books/month, priority processing |
| Publisher Plan | $99/month | 10 books/month, premium voices, bulk |

**Unit economics (80,000-word book):**
- ~480,000 characters
- ElevenLabs cost: ~$1.44 (at $3/1M chars on Creator plan)
- Charge user: ~$7–10/book
- Margin: ~85%

---

## 5. MVP Feature List

### 5.1 File Ingestion
- Supported formats: DOCX, PDF
- Drag-and-drop upload
- File browser fallback
- Max file size: 50MB
- Show file name and word count after upload
- Server-side parsing (mammoth for DOCX, pdfplumber for PDF)

### 5.2 Chapter Detection
- Auto-detect chapters from:
  - DOCX Heading 1 styles
  - "Chapter X" / "Chapter Name" regex patterns
  - Page breaks (PDF)
- Show detected chapter list with word counts
- Allow manual merge/split before generating
- Fallback: "no chapters found → treat as single track"

### 5.3 Voice Selection
- Surface ElevenLabs voice library (pre-filtered to narration/audiobook voices)
- 10–15 curated voices shown (male/female, accent variety)
- Voice preview: play 15-second sample per voice
- One voice per book (no per-chapter switching in MVP)

### 5.4 Audio Generation
- "Generate Audiobook" button triggers full conversion
- Real-time progress: per-chapter progress + overall %
- Processing runs server-side (UI stays responsive via WebSocket or polling)
- Cancel button mid-generation
- All TTS via ElevenLabs API

### 5.5 Export
- Output format: MP3, 192kbps (ACX minimum)
- Loudness normalized to ACX standard (−23 LUFS, −3dBTP peak) via ffmpeg
- One MP3 per chapter
- Download as ZIP (all chapters) or individual chapter downloads
- Files available for 7 days, then deleted from server

### 5.6 Auth & Accounts
- Sign up / login (email + password or Google OAuth)
- Dashboard showing past conversions + download links
- Usage tracking (characters used this month)
- Billing portal (Stripe)

### 5.7 Payment
- Stripe for payments
- Pay-per-book: charge at generation start
- Subscription: monthly via Stripe billing
- Free trial: no credit card required for first 10K characters

---

## 6. Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS | Web app |
| Backend | FastAPI (Python) | File processing, TTS pipeline |
| Auth | Clerk | Email + Google OAuth |
| DOCX parsing | mammoth (Python) | |
| PDF parsing | pdfplumber (Python) | |
| TTS | ElevenLabs API | MVP |
| TTS (v2) | Kokoro 82M (local/offline) | Post-MVP privacy tier — Python already in backend |
| Audio processing | ffmpeg (server-side) | WAV → MP3, loudness norm |
| Job queue | Inngest | Managed async jobs, works with Next.js + FastAPI |
| File storage | Cloudflare R2 | S3-compatible, zero egress fees |
| Database | PostgreSQL (Supabase) | Users, jobs, billing |
| Payments | Stripe | Pay-per-use + subscriptions |
| Hosting | Vercel (frontend) + Railway/Fly.io (FastAPI) | |

---

## 7. Project Structure

```
newBooktoAudiobook/
├── frontend/                  # Next.js 14 app
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Main UI (upload, voice, progress, download)
│   │   └── globals.css
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
├── backend/                   # FastAPI (Python)
│   ├── main.py                # Routes: /upload, /generate, /status, /download
│   ├── parser.py              # DOCX + PDF parsing + chapter detection
│   ├── tts.py                 # ElevenLabs API integration
│   ├── audio.py               # ffmpeg WAV → MP3 + loudness norm
│   ├── storage.py             # Cloudflare R2 (boto3)
│   └── requirements.txt
├── .env.example               # All required env vars
├── README.md
├── CLAUDE.md
└── tasks/
    ├── prd.md
    ├── todo.md
    └── lessons.md
```

## 8. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      BROWSER                                 │
│  Next.js frontend — upload, voice picker, progress, download │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────┐
│                      API LAYER                               │
│  Next.js API routes / FastAPI                                │
│  - Auth (Clerk)                                              │
│  - File upload → S3                                          │
│  - Job creation → Queue                                      │
│  - Stripe billing                                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    WORKER (async)                            │
│  BullMQ / Inngest job processor                              │
│  1. Pull file from S3                                        │
│  2. Parse DOCX/PDF → text + chapters                         │
│  3. Send each chapter to ElevenLabs API                      │
│  4. Receive audio → ffmpeg (loudness norm → MP3)             │
│  5. Upload MP3s to S3                                        │
│  6. Notify frontend (WebSocket / polling)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ElevenLabs API + S3 + PostgreSQL
```

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ElevenLabs API cost higher than expected | Medium | High | Rate-limit per user; estimate cost before generating; charge upfront |
| Large PDF parsing quality poor | Medium | Medium | Test with real books; fallback to raw text extraction |
| Chapter detection misses chapters | Medium | Medium | Show detected chapters before generating; allow manual edit |
| ElevenLabs rate limits on large books | Medium | Medium | Queue chapters sequentially; handle 429s with backoff |
| User uploads copyrighted books | Low | High | ToS clause; no responsibility for content |
| S3 storage cost for large files | Low | Low | Auto-delete after 7 days |
| ACX loudness not met | Medium | Medium | ffmpeg -af loudnorm in pipeline |

---

## 9. NOT in Scope (MVP)

| Feature | Reason Deferred |
|---------|----------------|
| Offline / local TTS (Kokoro) | v2 — privacy tier |
| Desktop app (Electron) | Web-first, add later if demand |
| Voice cloning | v2 |
| Multi-character voices | v2 |
| EPUB ingestion | v1.1 |
| ACX direct upload | Manual download works for MVP |
| Auto-chapter audio preview | v1.1 |
| M4B export (single file) | v1.1 |
| Windows/Mac desktop app | v2 |
| White-label / API access | v2 |

---

## 10. Build Sequence

### Phase 0 — Core Pipeline (Week 1, ~2 days)
- [ ] Next.js project scaffold + Tailwind
- [ ] File upload (DOCX + PDF) → S3
- [ ] DOCX/PDF parsing → raw text + chapter detection
- [ ] ElevenLabs API integration (text → MP3 per chapter)
- [ ] ffmpeg loudness normalization
- [ ] ZIP download of all chapters
- **Goal: End-to-end working pipeline, no auth, no billing**

### Phase 1 — Auth + Billing (Week 2)
- [ ] Clerk auth (email + Google)
- [ ] Stripe pay-per-book flow
- [ ] Free trial (10K chars, no card)
- [ ] User dashboard (past jobs + downloads)
- [ ] 7-day file expiry + S3 cleanup

### Phase 2 — Polish + Beta (Week 3)
- [ ] Voice library UI (curated ElevenLabs voices + preview)
- [ ] Real-time progress (WebSocket or polling)
- [ ] Chapter list UI (detect + manual edit)
- [ ] Error handling + retry UI
- [ ] Beta with 5 indie authors

### Phase 3 — Launch (Week 4)
- [ ] Bug fixes from beta
- [ ] Landing page + pricing page
- [ ] Launch on Product Hunt + Reddit (r/selfpublish)

---

## 11. Open Questions

- [x] Backend: Next.js + FastAPI (separate Python service) ✓
- [x] Job queue: Inngest ✓
- [x] Auth: Clerk ✓
- [x] Storage: Cloudflare R2 ✓
- [ ] ElevenLabs plan — Creator ($22/mo, 1M chars) vs Scale ($99/mo, 10M chars)

---

## 12. v2 Roadmap (Post-MVP)

| Feature | Description |
|---------|-------------|
| Offline tier | Kokoro TTS, runs in browser via WASM or downloadable desktop app |
| Voice cloning | Upload 1-min sample, clone for whole book |
| Multi-character | Assign different voices per character |
| EPUB support | Add to ingestion pipeline |
| Publisher dashboard | Batch conversion, team seats |
| White-label API | License the pipeline to publishers |
