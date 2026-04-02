import os
import json
from enum import Enum
# Se importarán las librerías oficiales de cada proveedor de manera perezosa (lazy load)
# para evitar que la aplicación truene si no instalan todas las librerías a la vez.

class ProveedorLLM(Enum):
    OPENAI = 'openai'
    GEMINI = 'gemini'
    GROQ = 'groq'

class LLMFactory:
    """
    Fábrica encargada de instanciar y conectar con el proveedor seleccionado por el administrador.
    Retorna siempre un JSON estandarizado con la misma estructura para la pregunta de Trivia.
    """
    
    @staticmethod
    def generar_trivia(proveedor: str, api_key: str):
        proveedor_normalizado = proveedor.lower().strip()
        
        # El Prompt del sistema (Instrucciones exactas)
        system_prompt = (
            "Eres un experto en la Copa Mundial de la FIFA y su historia. "
            "Genera una trivia de opción múltiple muy interesante pero no imposible. "
            "DEBES obligatoriamente responder ÚNICA Y EXCLUSIVAMENTE con un JSON válido, sin texto adicional, "
            "sin bloques markdown, solo el diccionario JSON con la siguiente estructura exacta: "
            "{\"pregunta\": \"Aquí va la pregunta\", \"opcion_a\": \"Opción 1\", \"opcion_b\": \"Opción 2\", "
            "\"opcion_c\": \"Opción 3\", \"opcion_d\": \"Opción 4\", \"opcion_correcta\": \"A\", "
            "\"explicacion\": \"Breve explicación deportiva e histórica de por qué es la correcta\"}"
        )
        
        try:
            if proveedor_normalizado == ProveedorLLM.OPENAI.value:
                return LLMFactory._solicitar_openai(api_key, system_prompt)
            elif proveedor_normalizado == ProveedorLLM.GEMINI.value:
                return LLMFactory._solicitar_gemini(api_key, system_prompt)
            elif proveedor_normalizado == ProveedorLLM.GROQ.value:
                return LLMFactory._solicitar_groq(api_key, system_prompt)
            else:
                raise ValueError(f"Proveedor '{proveedor}' no soportado por LLMFactory.")
                
        except Exception as e:
            print(f"Error generando trivia vía {proveedor_normalizado}: {e}")
            return None

    @staticmethod
    def _solicitar_openai(api_key: str, system_prompt: str):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Falta instalar librería 'openai'. Ejecuta: pip install openai")
            
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # o el modelo deseado
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Dame una trivia nueva hoy sobre mundiales de fútbol."}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)

    @staticmethod
    def _solicitar_gemini(api_key: str, system_prompt: str):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Falta instalar librería 'google-generativeai'. Ejecuta: pip install google-generativeai")
            
        genai.configure(api_key=api_key)
        # model = genai.GenerativeModel('gemini-pro') 
        # Importante: para JSON mode se recomienda gemini-1.5-flash
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content("Dame una trivia nueva hoy sobre mundiales de fútbol.")
        return json.loads(response.text)

    @staticmethod
    def _solicitar_groq(api_key: str, system_prompt: str):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Falta instalar librería 'groq'. Ejecuta: pip install groq")
            
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Dame una trivia nueva hoy sobre mundiales de fútbol."}
            ],
            model="llama3-8b-8192", # O "mixtral-8x7b-32768"
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
