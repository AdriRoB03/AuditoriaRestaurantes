import os
import sqlite3
import hashlib
import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

def obtener_resenas_gratis(url_restaurante, api_token):
    print("Conectando con Apify (esto puede tardar un minuto)...")
    
    # Inicializamos el cliente con la clave secreta
    client = ApifyClient(api_token)
    
    # Configuramos qué queremos extraer
    run_input = {
        "startUrls": [{"url": url_restaurante}],
        "maxReviews": 800, # Extraemos las reseñas
        "language": "es"
    }

    # Llamamos a un scraper público de Apify especializado en reseñas
    run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
    
    # Comprobamos cómo nos ha devuelto Apify los datos según la versión instalada
    if isinstance(run, dict):
        dataset_id = run.get("defaultDatasetId")
    else:
        # Si es un objeto (versiones nuevas), buscamos el ID con este método seguro
        dataset_id = getattr(run, "defaultDatasetId", getattr(run, "default_dataset_id"))
    
    # Recogemos los resultados usando el ID correcto
    resultados = client.dataset(dataset_id).iterate_items()
    
    resenas_limpias = []
    for resena in resultados:
        texto_resena = resena.get("text")
        
        # Filtramos primero para guardar solo las que tienen texto
        if texto_resena:
            fecha_resena = resena.get("publishedAtDate", "")
            
            # Creamos un ID anónimo basado matemáticamente en el texto y la fecha
            # Si se ejecuta 100 veces, esta fórmula siempre dará el mismo ID para la misma reseña
            string_base = f"{texto_resena}{fecha_resena}".encode('utf-8')
            id_constante = hashlib.md5(string_base).hexdigest()[:10]
            
            resena_limpia = {
                "id_cliente": f"Cliente_{id_constante}",
                "fecha": fecha_resena,
                "estrellas": resena.get("stars"),
                "texto": texto_resena
            }
            resenas_limpias.append(resena_limpia)

    return resenas_limpias

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    APIFY_TOKEN = os.getenv("APIFY_TOKEN")
    URL_RESTAURANTE = os.getenv("URL_RESTAURANTE")

    if not APIFY_TOKEN or not URL_RESTAURANTE:
        print("⚠️ Faltan tus claves. Revisa tu archivo .env")
    else:
        lista_resenas = obtener_resenas_gratis(URL_RESTAURANTE, APIFY_TOKEN)
        
        if lista_resenas:
            # Convertimos los datos en una tabla de Pandas
            df = pd.DataFrame(lista_resenas)
            
            # Lo guardamos en formato CSV (como backup)
            df.to_csv("raw_reviews.csv", index=False, encoding="utf-8")
            print(f"✅ ¡Éxito! Se han guardado {len(df)} reseñas anonimizadas en el backup 'raw_reviews.csv'")
            
            # --- NUEVA CONEXIÓN A LA BASE DE DATOS ---
            print("\n💾 Sincronizando con la base de datos SQLite...")
            conexion = sqlite3.connect("restaurantes.db")
            cursor = conexion.cursor()
            
            # Nos aseguramos de que la tabla existe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resenas (
                id_cliente TEXT PRIMARY KEY,
                fecha TEXT,
                estrellas INTEGER,
                texto TEXT,
                sentimiento TEXT,
                categoria TEXT,
                resumen TEXT
            )
            ''')
            
            nuevas_insertadas = 0
            
            for index, fila in df.iterrows():
                try:
                    # Insertamos solo las columnas básicas, el resto se quedan en NULL hasta que pase la IA
                    cursor.execute('''
                    INSERT INTO resenas (id_cliente, fecha, estrellas, texto)
                    VALUES (?, ?, ?, ?)
                    ''', (fila["id_cliente"], fila["fecha"], fila["estrellas"], fila["texto"]))
                    nuevas_insertadas += 1
                except sqlite3.IntegrityError:
                    # Si el id_cliente ya existe, significa que es una reseña vieja. La ignoramos.
                    pass
                    
            conexion.commit()
            conexion.close()
            
            print(f"✅ Sincronización completa: {nuevas_insertadas} reseñas NUEVAS listas para ser analizadas por IA.")
        else:
            print("❌ No se encontraron reseñas con texto o hubo un error.")