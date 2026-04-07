# Book to Audiobook — Phase 0

Offline-first web app that converts books (DOCX/PDF) into professional audiobooks using ElevenLabs AI voices.

## Prerequisites

- Node.js 18+
- Python 3.12+
- ffmpeg (`brew install ffmpeg` on macOS)

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` in the project root and fill in:
- `ELEVENLABS_API_KEY` — get from elevenlabs.io
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` — Cloudflare R2 credentials

Also create `backend/.env` and `frontend/.env.local` with the same values (backend needs ElevenLabs + R2, frontend needs `NEXT_PUBLIC_API_URL=http://localhost:8000`).

### 2. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Locally

**Backend (terminal 1):**
```bash
cd backend
uvicorn main:app --reload
```

**Frontend (terminal 2):**
```bash
cd frontend
npm run dev
```

Open http://localhost:3000

## Usage

1. Drag and drop a DOCX or PDF file
2. Select an AI voice from the dropdown
3. Click "Generate Audiobook"
4. Watch progress as each chapter is processed
5. Download the ZIP when complete

## Phase 0 Limitations

- No user authentication
- No database (jobs stored in memory)
- Synchronous processing (one chapter at a time)
- No billing or usage limits
- Jobs lost on server restart

These will be addressed in Phase 1.
