import streamlit as st
import whisper
from pydub import AudioSegment
import tempfile
import json
import os

st.title("Speech-to-Text with Translation")

uploaded_file = st.file_uploader("Upload MP3", type=["mp3"])

def save_json(data, filename="transcription.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filename

if uploaded_file:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(uploaded_file.read())
        mp3_path = tmp.name

    audio = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")

    st.audio(wav_path, format="audio/wav")

    model = whisper.load_model("base")

    # Use 'translate' to automatically convert Hindi speech to English text
    result = model.transcribe(wav_path, task="translate")

    text = result["text"].strip()
    sentences = [s.strip() for s in text.split(".") if s]

    speakers = ["client", "speaker"]
    transcription = []

    for i, sentence in enumerate(sentences):
        transcription.append({
            "speaker": speakers[i % 2],
            "text": sentence
        })

    st.header("Transcription JSON")
    st.json(transcription)

    json_file = save_json(transcription)

    with open(json_file, "rb") as f:
        st.download_button("Download JSON", f, file_name=json_file, mime="application/json")

    try:
        os.remove(mp3_path)
        os.remove(wav_path)
    except:
        pass
