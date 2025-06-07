import streamlit as st
from pydub import AudioSegment
import whisper
import tempfile
import json
import os

st.title("English Speech-to-Text with Hindi Translation & Speaker Labels")

uploaded_file = st.file_uploader("Upload MP3 audio file", type=["mp3"])

def save_json(data, filename="transcription.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filename

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        tmp_mp3.write(uploaded_file.read())
        tmp_mp3_path = tmp_mp3.name

    audio = AudioSegment.from_mp3(tmp_mp3_path)
    tmp_wav_path = tmp_mp3_path.replace(".mp3", ".wav")
    audio.export(tmp_wav_path, format="wav")

    st.audio(tmp_wav_path, format="audio/wav")

    # Load Whisper model
    model = whisper.load_model("base")

    # Translate to English (auto-detect language and translate)
    result = model.transcribe(tmp_wav_path, task="translate")

    # For demo: Mock speaker segmentation by splitting text roughly
    # Split transcription text into chunks (fake speaker turns)
    text = result["text"].strip()
    sentences = text.split(". ")

    # Assign speakers alternately: client, speaker, client, speaker...
    speakers = ["client", "speaker"]
    transcription_json = []
    for i, sentence in enumerate(sentences):
        if sentence:
            transcription_json.append({
                "speaker": speakers[i % 2],
                "text": sentence.strip()
            })

    # Show transcription JSON nicely
    st.header("Transcription JSON")
    st.json(transcription_json)

    # Save JSON to file
    json_filename = save_json(transcription_json)

    # Provide download link
    with open(json_filename, "rb") as f:
        st.download_button("Download Transcription JSON", f, file_name=json_filename, mime="application/json")

    # Optional: remove temp files
    try:
        os.remove(tmp_mp3_path)
        os.remove(tmp_wav_path)
    except Exception:
        pass
