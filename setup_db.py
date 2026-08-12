import sqlite3
import pandas as pd
import os

print("⚙️ Configurando base de datos SQLite...")

# Nos conectamos a la base de datos (Python creará el archivo automáticamente)
conexion = sqlite3.connect("restaurantes.db")
cursor = conexion.cursor()

# Creamos la tabla con las columnas exactas que necesitamos
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

# Leemos tu archivo actual que se quedó a medias
if os.path.exists("analyzed_reviews.csv"):
    df = pd.read_csv("analyzed_reviews.csv")
    
    insertadas = 0
    for index, fila in df.iterrows():
        # Si la IA dio "Error" en los últimos lotes, lo guardamos como vacío (None)
        # Así, nuestro nuevo programa sabrá que tiene que procesar estas reseñas pendientes.
        sentimiento = fila["Sentimiento"] if fila["Sentimiento"] not in ["Error", "Desconocido"] else None
        categoria = fila["Categoria"] if fila["Categoria"] not in ["Error", "Desconocido"] else None
        resumen = fila["Resumen"] if fila["Resumen"] not in ["Error", "Desconocido"] else None
        
        try:
            cursor.execute('''
            INSERT INTO resenas (id_cliente, fecha, estrellas, texto, sentimiento, categoria, resumen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fila["id_cliente"], fila["fecha"], fila["estrellas"], fila["texto"], sentimiento, categoria, resumen))
            insertadas += 1
        except sqlite3.IntegrityError:
            # Si la reseña ya existe en la base de datos (por su ID), la ignoramos
            pass 

    conexion.commit()
    print(f"✅ ¡Éxito! Se ha creado 'restaurantes.db' y se han insertado {insertadas} reseñas.")
    print("Las reseñas que dieron error ahora están marcadas como pendientes de analizar.")
else:
    print("❌ No se ha encontrado el archivo 'analyzed_reviews.csv'.")

conexion.close()