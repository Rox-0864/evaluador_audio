import streamlit as st
import requests
from groq import Groq # Solo necesitamos la clase Groq
import os
import io
import spech_to_text 

# --- Funciones para interactuar con la API de Groq ---

def evaluar_con_groq(api_key, pregunta, respuesta_estudiante):
    """
    Función que evalúa respuestas de estudiantes usando la API de Groq.
    
    Args:
        api_key (str): Clave de API de Groq para autenticación.
        pregunta (str): La pregunta que se hizo al estudiante.
        respuesta_estudiante (str): La respuesta que dio el estudiante (en texto).
    
    Returns:
        str: Feedback del evaluador o mensaje de error.
    """
    
    # URL del endpoint de la API de Groq para chat completions (compatible con OpenAI)
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Headers necesarios para la petición HTTP
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Estructura de datos que se envía a la API para la evaluación
    data = {
        "messages": [
            # 1. MENSAJE DEL SISTEMA: Define el comportamiento del evaluador
            {
                "role": "system",
                "content": "Eres un evaluador experto en ciencia de datos. Evalúa si la respuesta es correcta y completa. Háblame directamente como si fueras mi profesor, usando frases como 'Fallaste en...', 'Te faltó mencionar...', 'Mejora en...', 'Excelente, cubriste...', etc."
            },
            
            # 2. EJEMPLO DE PREGUNTA CON RESPUESTA MALA
            {
                "role": "user",
                "content": "Pregunta: ¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?\nRespuesta del estudiante: Es necesario preprocesar los datos porque hay que limpiarlos antes de usarlos en el modelo. Los datos sucios no sirven y pueden tener errores."
            },
            
            # 3. EJEMPLO DE FEEDBACK DEL EVALUADOR
            {
                "role": "assistant",
                "content": "Fallaste en tu respuesta: solo mencionas 'limpiar datos' de forma muy general. Te faltó explicar qué tipo de limpieza (valores faltantes, outliers), procesos como normalización y codificación de variables categóricas."
            },
            
            # 4. LA NUEVA PREGUNTA A EVALUAR
            {
                "role": "user",
                "content": f"Pregunta: {pregunta}\nRespuesta: {respuesta_estudiante}"
            }
        ],
        
        # Configuración del modelo
        "model": "llama3-8b-8192",
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        evaluacion = response.json()['choices'][0]['message']['content']
        
        return evaluacion
        
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con la API de Groq para evaluación: {e}"

# --- Función para Text-to-Speech con Groq (TTS) ---
def texto_a_audio_groq(api_key, texto, output_filename="feedback_profesor.mp3"):
    """
    Función que convierte texto a audio usando la API de Groq (TTS).
    
    Args:
        api_key (str): Clave de API de Groq para autenticación.
        texto (str): El texto que se desea convertir a voz.
        output_filename (str): Nombre del archivo donde se guardará el audio.
        
    Returns:
        str: La ruta al archivo de audio generado o None si hay un error.
    """
    client = Groq(api_key=api_key) # Usa el cliente de Groq
    try:
        # Asegúrate de usar una voz válida de Groq (ej. "Fritz-PlayAI" o cualquiera de la lista que te dio el error)
        response = client.audio.speech.create(
            model="playai-tts", # Modelo de Text-to-Speech de Groq
            voice="Fritz-PlayAI", # ¡IMPORTANTE! Elige una voz de la lista que Groq acepta para 'playai-tts'
            input=texto,
        )
        # Guarda el audio en un archivo temporal
        with open(output_filename, "wb") as f:
            f.write(response.read()) # <-- CORRECCIÓN AQUÍ: Usamos .read() para obtener los bytes
        return output_filename
    except Exception as e:
        st.error(f"Error al generar audio con Groq TTS: {e}")
        return None

# --- Configuración de la aplicación Streamlit ---

st.set_page_config(layout="wide")

st.markdown("<h3 style='text-align: center; margin-bottom: 0px'>¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?</h1><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([49, 2, 49])

# --- Manejo de la API Key con st.secrets (Solo Groq) ---
try:
    GROQ_API_KEY = st.secrets['groq']["GROQ_API_KEY"]
except KeyError:
    st.error("¡Error! La clave 'GROQ_API_KEY' no se encontró en .streamlit/secrets.toml o st.secrets.")
    st.stop() # Detiene la ejecución si la clave no está presente


# --- Columna izquierda - Alumno ---
with col1:
    st.markdown('<br>'*1, unsafe_allow_html=True)
    st.image("https://images.openai.com/thumbnails/bc4fd35a4319dcd1189035f5f2adbc1e.jpeg", width=200) # [Image of a male student avatar]
    st.write("**Alumno**")
    
    audio_bytes = st.audio_input("Presiona para grabar tu respuesta", label_visibility="visible")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        pregunta_actual = "¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?"
        
        st.info("Transcribiendo tu respuesta con Groq Whisper...")
        # Llama a la función para transcribir el audio a texto (con Groq)
        texto_respuesta_estudiante = spech_to_text.transcribir_audio_groq(audio_bytes.read(), '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')
        
        if texto_respuesta_estudiante:
            st.write(f"**Tu respuesta (texto):** {texto_respuesta_estudiante}")
            
            st.session_state['respuesta_transcrita'] = texto_respuesta_estudiante
            st.session_state['pregunta_actual'] = pregunta_actual
            
            st.success("Audio transcrito y listo para evaluar.")
        else:
            st.error("No se pudo transcribir el audio. Intenta de nuevo.")

# --- Columna derecha - Profesor ---        
with col3:
    st.image("https://cdn-icons-png.flaticon.com/512/1869/1869679.png", width=200) # [Image of a male teacher avatar]
    st.write("**Profesor**")
    
    if 'evaluacion_audio_path' in st.session_state and os.path.exists(st.session_state['evaluacion_audio_path']):
        try:
            audio_file_feedback = open(st.session_state['evaluacion_audio_path'], "rb")
            st.audio(audio_file_feedback.read(), format='audio/mp3')
            audio_file_feedback.close()
        except Exception as e:
            st.error(f"Error al cargar el audio del profesor: {e}")
    else:
        st.write("Esperando la respuesta del alumno para evaluar...")

# --- Botones de acción centrados ---
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("**Evaluar respuesta**", use_container_width=True):
        if 'respuesta_transcrita' in st.session_state and 'pregunta_actual' in st.session_state:
            with st.spinner("Evaluando la respuesta..."):
                # Llama a la función de evaluación (con Groq)
                feedback_texto = evaluar_con_groq(
                    GROQ_API_KEY,
                    st.session_state['pregunta_actual'],
                    st.session_state['respuesta_transcrita']
                )
            
            if feedback_texto:
                st.write(f"**Feedback del profesor:** {feedback_texto}")
                
                with st.spinner("Generando audio del feedback..."):
                    output_audio_path = "feedback_profesor.mp3"
                    # Llama a la función de TTS de Groq
                    audio_path = texto_a_audio_groq(GROQ_API_KEY, feedback_texto, output_audio_path)
                    
                    if audio_path:
                        st.session_state['evaluacion_audio_path'] = audio_path
                        st.success("Feedback generado en audio.")
                        st.rerun()
                    else:
                        st.error("No se pudo generar el audio del feedback.")
            else:
                st.error("No se pudo obtener feedback de Groq.")
        else:
            st.warning("Por favor, graba la respuesta del estudiante primero.")
            
    if st.button("**Próxima pregunta**", use_container_width=True):
        if 'respuesta_transcrita' in st.session_state:
            del st.session_state['respuesta_transcrita']
        if 'pregunta_actual' in st.session_state:
            del st.session_state['pregunta_actual']
        
        if 'evaluacion_audio_path' in st.session_state and os.path.exists(st.session_state['evaluacion_audio_path']):
            os.remove(st.session_state['evaluacion_audio_path'])
            del st.session_state['evaluacion_audio_path']

        st.success("Siguiente pregunta cargada (estado reiniciado).")
        st.rerun() # <-- CORRECCIÓN AQUÍ: 
