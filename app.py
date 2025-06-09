import os
import tempfile
import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr
import time

# Configure the page
st.set_page_config(
    page_title="Audio to Text Extractor",
    page_icon="🎤",
    layout="centered"
)

def main():
    st.title("🎤 Audio to Text Extractor")
    st.markdown("Upload an MP3 file to extract text from audio")

    # Initialize session state
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Extract Text"):
            with st.spinner("Processing audio..."):
                try:
                    # Create temporary files
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                        tmp_mp3.write(uploaded_file.read())
                        mp3_path = tmp_mp3.name
                    
                    # Convert MP3 to WAV
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                        wav_path = tmp_wav.name
                        sound = AudioSegment.from_mp3(mp3_path)
                        sound.export(wav_path, format="wav")
                    
                    # Initialize recognizer
                    r = sr.Recognizer()
                    
                    # Process audio in chunks
                    full_text = ""
                    audio_file = sr.AudioFile(wav_path)
                    
                    with audio_file as source:
                        duration = source.DURATION
                        chunk_size = 30  # seconds
                        total_chunks = int(duration // chunk_size) + 1
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(total_chunks):
                            # Read chunk
                            audio = r.record(source, duration=chunk_size)
                            
                            # Recognize chunk
                            try:
                                text = r.recognize_google(audio)
                                full_text += " " + text
                            except sr.UnknownValueError:
                                st.warning(f"Could not understand chunk {i+1}")
                            except sr.RequestError as e:
                                st.error(f"API error: {e}")
                                break
                            
                            # Update progress
                            progress = (i + 1) / total_chunks
                            progress_bar.progress(progress)
                            status_text.text(f"Processing chunk {i+1} of {total_chunks}")
                    
                    st.session_state.extracted_text = full_text.strip()
                    st.success("Text extraction complete!")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Please ensure FFmpeg is installed on your system.")
                
                finally:
                    # Clean up temporary files
                    if 'mp3_path' in locals() and os.path.exists(mp3_path):
                        os.unlink(mp3_path)
                    if 'wav_path' in locals() and os.path.exists(wav_path):
                        os.unlink(wav_path)
    
    # Display results
    if st.session_state.extracted_text:
        st.subheader("Extracted Text")
        st.text_area("Result", st.session_state.extracted_text, height=300)
        
        st.download_button(
            "Download Text",
            st.session_state.extracted_text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
