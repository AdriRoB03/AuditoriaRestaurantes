import os
import time
import json
import pandas as pd
import sqlite3
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
    print("⚙️ Conectando a la base de datos SQLite...")
    conexion = sqlite3.connect("restaurantes.db")
    cursor = conexion.cursor()
    
    # Solo pedimos las reseñas que NO tienen sentimiento o que fallaron antes
    cursor.execute("SELECT id_cliente, texto FROM resenas WHERE sentimiento IS NULL OR sentimiento = 'Error'")
    pendientes = cursor.fetchall()
    
    if not pendientes:
        print("✅ No hay reseñas nuevas para analizar. ¡Todo está al día!")
    else:
        print(f"🤖 Se han encontrado {len(pendientes)} reseñas pendientes. Iniciando análisis...")
        
        tamano_lote = 10
        for i in range(0, len(pendientes), tamano_lote):
            lote = pendientes[i:i+tamano_lote]
            textos_lote = [fila[1] for fila in lote]
            ids_lote = [fila[0] for fila in lote]
            
            print(f"Procesando reseñas {i+1} a {min(i+tamano_lote, len(pendientes))} de {len(pendientes)}...")
            
            resultados = analizar_lote_con_ia(textos_lote)
            
            # Verificamos que la IA nos devuelve exactamente las que le pedimos
            if len(resultados) == len(lote):
                for j in range(len(lote)):
                    res = resultados[j]
                    # Solo actualizamos si no devolvió un error masivo
                    if res.get("sentimiento") != "Error":
                        cursor.execute('''
                            UPDATE resenas 
                            SET sentimiento = ?, categoria = ?, resumen = ? 
                            WHERE id_cliente = ?
                        ''', (res.get("sentimiento"), res.get("categoria"), res.get("resumen"), ids_lote[j]))
                
                conexion.commit() # PUNTO DE GUARDADO
                print("💾 Lote guardado con éxito.")
            else:
                print("⚠️ Descuadre en la respuesta de la IA. Saltando lote por seguridad.")
            
            # Pausa para la API
            if i + tamano_lote < len(pendientes):
                time.sleep(10)
        
        print("\n✅ ¡Análisis incremental completado!")
        
    conexion.close()