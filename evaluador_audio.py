import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import pandas as pd
import json
import os
from fpdf import FPDF

st.set_page_config(page_title="Evaluador por Voz", layout="centered")

# Cargar preguntas desde JSON
with open("preguntas.json", "r", encoding="utf-8") as f:
    preguntas = json.load(f)

if "resultados" not in st.session_state:
    st.session_state.resultados = []

def reproducir_audio(texto, lang="es"):
    tts = gTTS(text=texto, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio = AudioSegment.from_mp3(fp.name)
        play(audio)

def transcribir_audio(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = r.record(source)
        try:
            texto = r.recognize_google(audio_data, language="es-ES")
            return texto
        except sr.UnknownValueError:
            return "[No se pudo entender el audio]"
        except sr.RequestError as e:
            return f"[Error del servicio de reconocimiento de voz: {e}]"

st.title("🎓 Evaluador de Python por Voz")

pregunta_idx = st.number_input("Selecciona la pregunta", min_value=0, max_value=len(preguntas)-1, step=1)
pregunta = preguntas[pregunta_idx]

st.markdown(f"### Pregunta: {pregunta['pregunta']}")
if st.button("🔊 Escuchar pregunta"):
    reproducir_audio(pregunta["pregunta"])

uploaded_file = st.file_uploader("🎤 Sube tu respuesta grabada (.wav)", type=["wav"])
respuesta_transcrita = ""

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        respuesta_transcrita = transcribir_audio(tmp.name)

    st.markdown("### ✍️ Respuesta transcrita:")
    st.write(respuesta_transcrita)

    if st.button("✅ Evaluar respuesta"):
        es_correcta = respuesta_transcrita.strip().lower() == pregunta["respuesta"].strip().lower()
        resultado = {
            "pregunta": pregunta["pregunta"],
            "respuesta_esperada": pregunta["respuesta"],
            "respuesta_alumno": respuesta_transcrita,
            "correcta": es_correcta
        }
        st.session_state.resultados.append(resultado)
        st.success("✅ Respuesta correcta" if es_correcta else "❌ Respuesta incorrecta")

if st.session_state.resultados:
    st.markdown("## 📊 Resultados acumulados")
    df_resultados = pd.DataFrame(st.session_state.resultados)
    st.dataframe(df_resultados)

    if st.button("💾 Exportar CSV"):
        df_resultados.to_csv("resultados.csv", index=False)
        st.success("Archivo CSV generado: resultados.csv")

    if st.button("📄 Exportar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Resultados de la Evaluación", ln=True, align="C")
        for r in st.session_state.resultados:
            pdf.multi_cell(0, 10, txt=f"Pregunta: {r['pregunta']}
Esperada: {r['respuesta_esperada']}
Alumno: {r['respuesta_alumno']}
Correcta: {r['correcta']}
")
        pdf.output("resultados.pdf")
        st.success("Archivo PDF generado: resultados.pdf")