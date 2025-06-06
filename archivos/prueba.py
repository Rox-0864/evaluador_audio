import streamlit as st
import assemblyai as aai

st.title('Prueba')
audio=r'C:\Users\nico\OneDrive\Desktop\BootcampXperience\bx_project\evaluador_audio\tiktokio.com_CrZQB48bbtDTCQeej5Uf.mp3'
# audio= st.audio_input('Empieza a hablar', label_visibility='visible')
transcribe= aai.Transcriber()
config= aai.TranscriptionConfig(language_code='es')

transcripcion= aai.Transcriber(config=config).transcribe(audio)
st.write(transcripcion.text)