import base64
import requests
import json
from django.shortcuts import render
from django.conf import settings

def index(request):
    json_result = None
    error_message = None

    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            
            # 1. Convertir imagen a Base64
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 2. Configurar la petición a Perplexity
            # NOTA: Asegúrate de usar el modelo correcto que soporte visión.
            # Los modelos "sonar" suelen ser de búsqueda de texto. 
            # Si Perplexity usa endpoints compatibles con OpenAI, el formato es el siguiente:
            
            headers = {
                "Authorization": os.getenv('perplexity_secret_key'), 
                "Content-Type": "application/json"
            }

            payload = {
                "model": "sonar-pro", # O el modelo específico que uses de Perplexity/Sonar Vision
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image following the system instructions."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1 # Bajo para asegurar JSON estricto
            }

            # 3. Enviar a la API
            response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload)
            # --- AÑADE ESTO PARA DEPURAR ---
            if response.status_code != 200:
                print("================ ERROR API PERPLEXITY ================")
                print(response.text) # ESTO NOS DIRÁ LA CAUSA EXACTA
                print("======================================================")
            # -------------------------------
            response.raise_for_status()
            
            # 4. Procesar respuesta
            api_data = response.json()
            content = api_data['choices'][0]['message']['content']
            
            # Limpieza básica por si la IA añade bloques de código Markdown
            content_clean = content.replace("```json", "").replace("```", "").strip()
            
            # Validamos que sea JSON real antes de enviarlo al front
            json_object = json.loads(content_clean)
            json_result = json.dumps(json_object, indent=2)

        except Exception as e:
            error_message = f"Error procesando la imagen: {str(e)}"

    return render(request, 'index.html', {'json_result': json_result, 'error': error_message})
