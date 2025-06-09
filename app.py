import streamlit as st
from pydub import AudioSegment
import whisper
import tempfile

st.title("Shrishail english Speech-to-Text from MP3")

uploaded_file = st.file_uploader("Upload an MP3 audio file", type=["mp3"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        tmp_mp3.write(uploaded_file.read())
        tmp_mp3_path = tmp_mp3.name

    audio = AudioSegment.from_mp3(tmp_mp3_path)
    tmp_wav_path = tmp_mp3_path.replace(".mp3", ".wav")
    audio.export(tmp_wav_path, format="wav")

    st.audio(tmp_wav_path, format="audio/wav")

    model = whisper.load_model("base")
    result = model.transcribe(tmp_wav_path, language="en")

    st.header("Transcription")
    st.write(result["text"])
