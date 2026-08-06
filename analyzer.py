import os
import time
import json
import pandas as pd
from google import genai
from dotenv import load_dotenv

# Cargamos las claves
load_dotenv()

# Configuramos la conexión con Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("⚠️ Falta la GEMINI_API_KEY en tu archivo .env")

client = genai.Client(api_key=api_key)

def analizar_lote_con_ia(lista_textos):
    """Esta función recibe una LISTA de 10 reseñas y devuelve una LISTA de 10 resultados"""
    
    # Preparamos el texto del lote enumerando las reseñas (Reseña 1: ..., Reseña 2: ...)
    texto_lote = ""
    for i, texto in enumerate(lista_textos):
        texto_lote += f"Reseña {i+1}: {texto}\n"
    
    # Le pedimos a la IA que nos devuelva un "Array" (una lista) de JSONs
    prompt = f"""
    Eres un analista experto. Voy a pasarte un lote de reseñas.
    Devuelve ÚNICAMENTE un array JSON válido (una lista de objetos entre corchetes []).
    El array debe tener exactamente {len(lista_textos)} elementos, en el mismo orden exacto que te los paso.
    Cada objeto del JSON debe tener estas claves:
    - "sentimiento": "Positivo", "Negativo" o "Neutral".
    - "categoria": "Comida", "Servicio", "Precio", "Ambiente" u "Otro".
    - "resumen": Un resumen en máximo 5 palabras.
    
    Aquí están las reseñas:
    {texto_lote}
    """
    
    try:
        # Enviamos la petición a la IA
        respuesta = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        
        # Limpiamos la respuesta (a veces la IA pone "```json" al principio)
        texto_limpio = respuesta.text.strip().replace("```json", "").replace("```", "")
        
        # Convertimos el texto JSON en un diccionario de Python
        datos_json = json.loads(texto_limpio)
        return datos_json
        
    except Exception as e:
        print(f"Error en el lote: {e}")
        # Si algo falla en este bloque de 10, devolvemos 10 errores para no descuadrar la tabla
        return [{"sentimiento": "Error", "categoria": "Error", "resumen": "Error"} for _ in lista_textos]

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    print("Abriendo raw_reviews.csv...")
    df = pd.read_csv("raw_reviews.csv")
    
    resultados_totales = []
    
    # Vamos a enviar las reseñas de 10 en 10
    tamano_lote = 10 
    
    print(f"🤖 Analizando {len(df)} reseñas por LOTES de {tamano_lote}... (Mucho más rápido y sin gastar cuota)")
    
    for i in range(0, len(df), tamano_lote):
        # Recortamos 10 reseñas de la tabla
        lote_actual = df["texto"].iloc[i:i+tamano_lote].tolist()
        print(f"Procesando reseñas de la {i+1} a la {min(i+tamano_lote, len(df))}...")
        
        # Se las pasamos a la IA
        respuestas_lote = analizar_lote_con_ia(lote_actual)
        
        # Comprobamos por seguridad que la IA nos haya devuelto 10 respuestas exactas
        if len(respuestas_lote) == len(lote_actual):
            resultados_totales.extend(respuestas_lote)
        else:
            print("⚠️ La IA se ha saltado alguna reseña. Rellenando con errores para no romper el programa.")
            for _ in lote_actual:
                resultados_totales.append({"sentimiento": "Error", "categoria": "Error", "resumen": "Error"})
        
        # Pequeña pausa de seguridad de 10 segundos entre paquete y paquete
        time.sleep(10) 
        
    # Añadimos los resultados (que ahora son listas) a nuestra tabla
    df["Sentimiento"] = [r.get("sentimiento") for r in resultados_totales]
    df["Categoria"] = [r.get("categoria") for r in resultados_totales]
    df["Resumen"] = [r.get("resumen") for r in resultados_totales]
    
    df.to_csv("analyzed_reviews.csv", index=False, encoding="utf-8")
    print("\n✅ ¡Análisis por lotes completado! Se ha actualizado 'analyzed_reviews.csv'")