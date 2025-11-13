from gtts import gTTS
import os
import time

def generate_audio(summary_text, symbol):
    """
    Generates a text-to-speech MP3 file from the given summary text.
    Saves it under backend/static/audio and returns the relative Flask URL.
    """
    # Get the root directory of the project
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Define audio directory relative to project root
    audio_dir = os.path.join(project_root, "backend", "static", "audio")
    os.makedirs(audio_dir, exist_ok=True)

    # Handle empty summaries safely
    if not summary_text or not summary_text.strip():
        summary_text = "No summary text available for this stock."

    # Create unique filename
    filename = f"{symbol}_{int(time.time())}.mp3"
    filepath = os.path.join(audio_dir, filename)

    try:
        # Convert text to speech
        tts = gTTS(summary_text)
        tts.save(filepath)

        # Return path Flask can serve
        return f"/static/audio/{filename}"

    except Exception as e:
        print("⚠️ TTS generation failed:", e)
        return None
