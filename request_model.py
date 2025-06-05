import requests

def evaluar_con_groq(api_key, pregunta, respuesta_estudiante):
    """
    Función que evalúa respuestas de estudiantes usando la API de Groq
    
    Args:
        api_key (str): Clave de API de Groq para autenticación
        pregunta (str): La pregunta que se hizo al estudiante
        respuesta_estudiante (str): La respuesta que dio el estudiante
    
    Returns:
        str: Feedback del evaluador o mensaje de error
    """
    
    # URL del endpoint de la API de Groq (compatible con OpenAI)
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Headers necesarios para la petición HTTP
    headers = {
        "Authorization": f"Bearer {api_key}",  # Autorización con la API key
        "Content-Type": "application/json"     # Especifica que enviamos JSON
    }
    
    # Estructura de datos que se envía a la API
    data = {
        "messages": [
            # 1. MENSAJE DEL SISTEMA: Define el comportamiento del evaluador
            {
                "role": "system",
                "content": "Eres un evaluador experto en ciencia de datos. Evalúa si la respuesta es correcta y completa. Háblame directamente como si fueras mi profesor, usando frases como 'Fallaste en...', 'Te faltó mencionar...', 'Mejora en...', 'Excelente, cubriste...', etc."
            },
            
            # 2. EJEMPLO DE PREGUNTA CON RESPUESTA MALA
            # Esto le enseña al modelo qué tipo de pregunta esperamos
            {
                "role": "user",
                "content": "Pregunta: ¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?\nRespuesta del estudiante: Es necesario preprocesar los datos porque hay que limpiarlos antes de usarlos en el modelo. Los datos sucios no sirven y pueden tener errores."
            },
            
            # 3. EJEMPLO DE FEEDBACK DEL EVALUADOR
            # Muestra al modelo cómo debe evaluar y dar feedback
            {
                "role": "assistant",
                "content": "Fallaste en tu respuesta: solo mencionas 'limpiar datos' de forma muy general. Te faltó explicar qué tipo de limpieza (valores faltantes, outliers), procesos como normalización y codificación de variables categóricas."
            },
            
            # 4. LA NUEVA PREGUNTA A EVALUAR
            # Aquí va la pregunta real que queremos evaluar
            {
                "role": "user",
                "content": f"Pregunta: {pregunta}\nRespuesta: {respuesta_estudiante}"
            }
        ],
        
        # Configuración del modelo
        "model": "llama3-8b-8192",  # Modelo de Groq a utilizar (Llama 3 8B)
        "temperature": 0.1          # Baja temperatura para respuestas más consistentes y menos creativas
    }
    
    # Manejo de la petición HTTP con control de errores
    try:
        # Envía la petición POST a la API de Groq
        response = requests.post(url, headers=headers, json=data)
        
        # Verifica si hubo algún error HTTP (4xx, 5xx)
        response.raise_for_status()
        
        # Extrae solo la respuesta del evaluador del JSON completo
        # La estructura es: response.json()['choices'][0]['message']['content']
        evaluacion = response.json()['choices'][0]['message']['content']
        
        return evaluacion
        
    except requests.exceptions.RequestException as e:
        # Captura cualquier error de red, HTTP o de la API
        return f"Error al conectar con la API: {e}"