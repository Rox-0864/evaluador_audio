import streamlit as st

# Configuración de la página en modo ancho
st.set_page_config(layout="wide")

st.markdown("<h3 style='text-align: center; margin-bottom: 0px'>¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?</h1><br>", unsafe_allow_html=True)

# Crear 3 columnas (centro muy estrecho)
col1, col2, col3 = st.columns([49, 2, 49])

# Columna izquierda - Alumno
with col1:
    st.markdown('<br>'*1, unsafe_allow_html=True)
    st.image("https://images.openai.com/thumbnails/bc4fd35a4319dcd1189035f5f2adbc1e.jpeg", width=200)
    st.write("**Alumno**")
    
    # Grabador de audio nativo
    audio_bytes = st.audio_input("Presiona para grabar", label_visibility="visible")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

# Columna derecha - Profesor        
with col3:
    st.image("https://cdn-icons-png.flaticon.com/512/1869/1869679.png", width=200)
    st.write("**Profesor**")
    
    # Audio pre-grabado (necesitas tener este archivo)
    audio_file = open("response.mp3", "rb")
    st.audio(audio_file.read(), format='audio/mp3')

# Botón centrado abajo
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("**Próxima pregunta**", use_container_width=True):
        st.success("Siguiente pregunta cargada")