import os
from elevenlabs.client import ElevenLabs


def get_client() -> ElevenLabs:
    """Get ElevenLabs client instance."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable not set")
    return ElevenLabs(api_key=api_key)


def generate_audio(text: str, voice_id: str) -> bytes:
    """
    Generate audio from text using ElevenLabs API.

    Args:
        text: The text to convert to speech
        voice_id: The ElevenLabs voice ID to use

    Returns:
        Raw audio bytes

    Raises:
        Exception: If API call fails
    """
    try:
        client = get_client()

        # Generate audio using eleven_multilingual_v2 model
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_192",
        )

        # Collect all audio chunks into bytes
        audio_bytes = b"".join(audio)

        return audio_bytes

    except Exception as e:
        raise Exception(f"ElevenLabs API error: {str(e)}")
