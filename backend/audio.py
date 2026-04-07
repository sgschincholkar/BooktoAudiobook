import os
from pathlib import Path


def process_audio(audio_bytes: bytes, output_path: str) -> str:
    """
    Write MP3 audio bytes directly to output path.
    ElevenLabs already outputs 192kbps MP3 at ACX-compatible quality —
    no re-encoding needed for Phase 0.

    Args:
        audio_bytes: MP3 audio bytes from ElevenLabs
        output_path: Desired output path for the MP3 file

    Returns:
        Path to the written MP3 file

    Raises:
        Exception: If writing fails
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        return output_path

    except Exception as e:
        raise Exception(f"Audio write error: {str(e)}")
