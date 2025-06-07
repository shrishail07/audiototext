import streamlit as st
from pydub import AudioSegment
import whisper
import tempfile
import json
import os

st.title("Speech-to-Text (English + Hindi Translation)")

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

    model = whisper.load_model("base")

    result = model.transcribe(tmp_wav_path, task="translate")

    text = result["text"].strip()
    sentences = text.split(". ")

    speakers = ["client", "speaker"]
    transcription_json = []
    for i, sentence in enumerate(sentences):
        if sentence:
            transcription_json.append({
                "speaker": speakers[i % 2],
                "text": sentence.strip()
            })

    st.header("Transcription JSON")
    st.json(transcription_json)

    json_filename = save_json(transcription_json)

    with open(json_filename, "rb") as f:
        st.download_button("Download Transcription JSON", f, file_name=json_filename, mime="application/json")

    try:
        os.remove(tmp_mp3_path)
        os.remove(tmp_wav_path)
    except Exception:
        pass
