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
    layout="wide"
)

# Function to check and install ffmpeg
def check_ffmpeg():
    try:
        # Try to use ffmpeg
        AudioSegment.converter = "ffmpeg"
        test_audio = AudioSegment.silent(duration=1000)
        test_audio.export(os.devnull, format="wav")
    except:
        st.error("""
        FFmpeg is not installed correctly. Please install it:
        
        - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
        - On MacOS: `brew install ffmpeg`
        - On Windows: Download from https://ffmpeg.org/download.html
        
        Then restart the app.
        """)
        return False
    return True

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    try:
        audio = AudioSegment.from_mp3(mp3_file_path)
        audio.export(wav_file_path, format="wav")
        return True
    except Exception as e:
        st.error(f"Error converting MP3 to WAV: {str(e)}")
        return False

# Function to process long audio files
def process_long_audio(audio_file_path, chunk_length_ms=30000):
    recognizer = sr.Recognizer()
    full_text = ""
    
    # Load the audio file
    audio = AudioSegment.from_wav(audio_file_path)
    duration_ms = len(audio)
    total_chunks = (duration_ms // chunk_length_ms) + 1
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(0, duration_ms, chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        
        # Save chunk to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_chunk:
            chunk.export(temp_chunk.name, format="wav")
            
            # Recognize the chunk
            with sr.AudioFile(temp_chunk.name) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    full_text += " " + text
                except sr.UnknownValueError:
                    st.warning(f"Could not understand audio in chunk {(i//chunk_length_ms)+1}")
                except sr.RequestError as e:
                    st.error(f"API request failed: {str(e)}")
                    return None
            
        # Update progress
        progress = min((i + chunk_length_ms) / duration_ms, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Processing... Chunk {(i//chunk_length_ms)+1} of {total_chunks}")
        
        # Clean up
        os.unlink(temp_chunk.name)
    
    progress_bar.empty()
    status_text.empty()
    
    return full_text.strip()

def main():
    st.title("🎤 Unlimited Audio to Text Extractor")
    st.markdown("Upload an MP3 file to extract text from audio")
    
    # Check for ffmpeg
    if not check_ffmpeg():
        return
    
    # Initialize session state
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    
    # File uploader
    uploaded_file = st.file_uploader("Upload MP3 file", type=["mp3"])
    
    # Process uploaded file
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')
        
        if st.button("Extract Text"):
            with st.spinner("Processing audio..."):
                # Create temporary files
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                    tmp_mp3.write(uploaded_file.read())
                    mp3_file_path = tmp_mp3.name
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                    wav_file_path = tmp_wav.name
                
                # Convert MP3 to WAV
                if convert_mp3_to_wav(mp3_file_path, wav_file_path):
                    # Process the audio
                    start_time = time.time()
                    extracted_text = process_long_audio(wav_file_path)
                    processing_time = time.time() - start_time
                    
                    if extracted_text:
                        st.session_state.extracted_text = extracted_text
                        st.success(f"Text extracted successfully in {processing_time:.2f} seconds!")
                
                # Clean up
                os.unlink(mp3_file_path)
                os.unlink(wav_file_path)
    
    # Display extracted text
    if st.session_state.extracted_text:
        st.subheader("Extracted Text")
        st.text_area("", st.session_state.extracted_text, height=300)
        
        # Download button
        st.download_button(
            label="Download Text",
            data=st.session_state.extracted_text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
