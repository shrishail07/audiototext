import streamlit as st
import whisper
from pydub import AudioSegment
import tempfile
import json

st.title("English Speech-to-Text (Supports Hindi + English)")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        tmp_mp3.write(uploaded_file.read())
        tmp_mp3_path = tmp_mp3.name

    # Convert MP3 to WAV
    audio = AudioSegment.from_mp3(tmp_mp3_path)
    tmp_wav_path = tmp_mp3_path.replace(".mp3", ".wav")
    audio.export(tmp_wav_path, format="wav")

    st.audio(tmp_wav_path, format="audio/wav")

    model = whisper.load_model("base")

    # Use language='en' and enable translation for mixed Hindi+English to English text
    result = model.transcribe(tmp_wav_path, language='en', task='translate')

    # Sample format with "speaker" and "client" (simple example)
    transcript_json = {
        "speaker": "Person 1",
        "client": result["text"]
    }

    st.header("Transcription")
    st.write(result["text"])

    st.header("Transcript JSON")
    st.json(transcript_json)

    # Optionally save to JSON file (local only, won't work on Streamlit Cloud)
    with open("transcript.json", "w") as f:
        json.dump(transcript_json, f)
