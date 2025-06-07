import streamlit as st
import tempfile
from faster_whisper import WhisperModel
import os
import json

st.title("🔊 Speech-to-English Text Transcriber")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    st.audio(tmp_path)

    model_size = "base"
    model = WhisperModel(model_size, compute_type="int8")

    st.info("Transcribing audio... Please wait.")
    segments, info = model.transcribe(tmp_path, beam_size=5)

    transcript = []
    for segment in segments:
        transcript.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })

    st.success("Transcription completed!")
    st.write("### Transcribed Text")
    for i, s in enumerate(transcript):
        speaker = "Client" if i % 2 == 0 else "Agent"
        st.markdown(f"**{speaker}:** {s['text']}")

    # Save to JSON
    json_output = {"transcript": transcript}
    json_file = os.path.splitext(tmp_path)[0] + ".json"
    with open(json_file, "w") as f:
        json.dump(json_output, f, indent=2)

    with open(json_file, "rb") as f:
        st.download_button("Download JSON", f, file_name="transcript.json")
