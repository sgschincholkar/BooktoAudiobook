import os
import uuid
import tempfile
import threading
import zipfile
from typing import Dict, List
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from parser import parse_docx, parse_pdf
from tts import generate_audio
from audio import process_audio
import storage

# Load environment variables
load_dotenv()

app = FastAPI(title="Book to Audiobook API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (Phase 0 - no database)
jobs: Dict[str, dict] = {}


class GenerateRequest(BaseModel):
    job_id: str
    voice_id: str


class ChapterStatus(BaseModel):
    title: str
    status: str
    progress: int = 0
    word_count: int = 0


class JobStatus(BaseModel):
    status: str
    chapters: List[ChapterStatus]
    error: str = None


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a book file (DOCX or PDF) and extract chapters.

    Returns:
        job_id: Unique identifier for this job
        chapters: List of detected chapters with metadata
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported"
            )

        # Validate file size (50MB max)
        contents = await file.read()
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File size must be under 50MB"
            )

        # Save to temp file
        suffix = ".pdf" if file.content_type == "application/pdf" else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(contents)
            temp_path = temp_file.name

        # Parse document
        try:
            if file.content_type == "application/pdf":
                chapters = parse_pdf(temp_path)
            else:
                chapters = parse_docx(temp_path)
        finally:
            # Clean up temp file
            os.unlink(temp_path)

        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            "status": "pending",
            "chapters": chapters,
            "chapter_statuses": [
                {
                    "title": ch["title"],
                    "status": "pending",
                    "progress": 0,
                    "word_count": ch["word_count"]
                }
                for ch in chapters
            ],
            "output_files": [],
            "error": None
        }

        return {
            "job_id": job_id,
            "chapters": jobs[job_id]["chapter_statuses"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def generate_audiobook(request: GenerateRequest):
    """
    Start audiobook generation for a job.

    Args:
        job_id: The job identifier from /upload
        voice_id: ElevenLabs voice ID to use

    Returns:
        job_id: The job identifier
    """
    try:
        if request.job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job = jobs[request.job_id]

        if job["status"] == "processing":
            raise HTTPException(status_code=400, detail="Job already processing")

        # Start background thread for generation
        thread = threading.Thread(
            target=process_job,
            args=(request.job_id, request.voice_id)
        )
        thread.start()

        return {"job_id": request.job_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Get the current status of a job.

    Returns:
        status: overall job status (pending/processing/completed/error)
        chapters: list of chapter statuses with progress
        error: error message if status is 'error'
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    return {
        "status": job["status"],
        "chapters": job["chapter_statuses"],
        "error": job.get("error")
    }


@app.get("/download/{job_id}")
async def download_audiobook(job_id: str):
    """
    Download the completed audiobook as a ZIP file.

    Returns:
        ZIP file containing all chapter MP3s
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed (status: {job['status']})"
        )

    try:
        # Create temporary ZIP file
        zip_path = tempfile.mktemp(suffix=".zip")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file_path in job["output_files"]:
                if os.path.exists(file_path):
                    # Add file to ZIP with just the filename (no path)
                    zipf.write(file_path, arcname=os.path.basename(file_path))

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"audiobook_{job_id}.zip",
            background=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_job(job_id: str, voice_id: str):
    """
    Background task to process all chapters of a job.
    Updates job status as it progresses.
    """
    try:
        job = jobs[job_id]
        job["status"] = "processing"

        output_dir = tempfile.mkdtemp()
        output_files = []

        for idx, chapter in enumerate(job["chapters"]):
            # Update chapter status
            job["chapter_statuses"][idx]["status"] = "processing"

            try:
                # Generate audio from text
                audio_bytes = generate_audio(chapter["text"], voice_id)

                # Process audio (convert to MP3 with normalization)
                output_filename = f"{idx + 1:02d}_{sanitize_filename(chapter['title'])}.mp3"
                output_path = os.path.join(output_dir, output_filename)
                process_audio(audio_bytes, output_path)

                output_files.append(output_path)

                # Mark chapter as done
                job["chapter_statuses"][idx]["status"] = "done"
                job["chapter_statuses"][idx]["progress"] = 100

            except Exception as e:
                job["chapter_statuses"][idx]["status"] = "error"
                raise e

        # All chapters complete
        job["status"] = "completed"
        job["output_files"] = output_files

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


def sanitize_filename(filename: str) -> str:
    """Remove or replace characters that are invalid in filenames."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()[:100]  # Limit length


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Book to Audiobook API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
