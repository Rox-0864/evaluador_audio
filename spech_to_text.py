import requests
import tempfile
import os

def transcribir_con_groq(audio_bytes, api_key):
    """
    Transcribe audio usando Groq Whisper API
    
    Args:
        audio_bytes: Bytes del archivo de audio
        api_key: API key de Groq
    
    Returns:
        str: Texto transcrito o mensaje de error
    """
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    
    try:
        # Preparar el archivo para envío
        with open(temp_file_path, "rb") as audio_file:
            files = {
                "file": ("audio.wav", audio_file, "audio/wav")
            }
            data = {
                "model": "whisper-large-v3"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
        # Limpiar archivo temporal
        os.unlink(temp_file_path)
        
        if response.status_code == 200:
            return response.json()["text"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return f"Error en transcripción: {str(e)}"