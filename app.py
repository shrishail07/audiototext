import streamlit as st
import whisper
import tempfile
import os
import json

# Load Whisper model once
@st.cache_resource
def load_model():
    return whisper.load_model("base")  # Options: tiny, base, small, medium, large

model = load_model()

st.title("🎧 English Speech to Text - Whisper")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        temp_audio_file.write(uploaded_file.read())
        temp_path = temp_audio_file.name

    st.write("Transcribing... Please wait.")
    result = model.transcribe(temp_path, language="en")
    st.success("Transcription Complete!")

    st.subheader("📝 Transcribed Text")
    st.write(result["text"])

    # Create a JSON object from the result
    json_data = {
        "transcription": result["text"]
    }

    # Convert JSON object to string and encode to bytes
    json_str = json.dumps(json_data, indent=4)
    json_bytes = json_str.encode('utf-8')

    # Download button
    st.download_button(
        label="⬇️ Download Transcription as JSON",
        data=json_bytes,
        file_name="transcription.json",
        mime="application/json"
    )

    # Optional: Delete temp file
    os.remove(temp_path)
