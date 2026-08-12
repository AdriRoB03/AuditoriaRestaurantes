# 🍽️ Auditoria de Restaurantes con IA

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Google_Gemini-AI-orange.svg)

Una herramienta construida en Python que automatiza la extracción, análisis y visualización de reseñas de restaurantes en Google Maps utilizando Inteligencia Artificial(NLP) y bases de datos relacionales.

En lugar de leer cientos de reseñas manualmente, este proyecto extrae los datos, utiliza NLP (Modelos de Lenguaje) para analizar el sentimiento y categorizar las quejas/alabanzas, y muestra los resultados en un Dashboard interactivo.

## 🚀 Características Principales

- **Web Scraping Automatizado:** Extracción de reseñas de Google Maps mediante Apify.
- **Anonimización de Datos:** Cumplimiento de privacidad sustituyendo nombres de usuarios por IDs únicos (UUID).
- **Almacenamiento Persistente:** Uso de **SQLite** como motor de base de datos relacional para garantizar la integridad de los datos.
- **Procesamiento NLP Incremental (Batching):** Integración con la API de Google Gemini (`gemini-3.5-flash-lite`). El script procesa reseñas por lotes (10 a la vez) y solo analiza los datos nuevos, optimizando el uso y los costes de la API. Clasifica por:
  - **Sentimiento:** Positivo, Negativo o Neutral.
  - **Categoría:** Comida, Servicio, Precio, Ambiente, u Otro.
  - **Resumen:** Síntesis de la reseña en máximo 5 palabras.
- **Dashboard Interactivo:** Panel visual construido con Streamlit y Plotly para la toma de decisiones de negocio.

## ⚙️ Instalación y Uso Local

Sigue estos pasos para ejecutar el proyecto en tu propio ordenador:

### 1. Clonar el repositorio e inicializar el entorno

    git clone [https://github.com/TU_USUARIO/AuditoriaRestaurantes.git](https://github.com/TU_USUARIO/AuditoriaRestaurantes.git)
    cd AuditoriaRestaurantes

    # Crear entorno virtual
    python -m venv venv

    # Activar entorno (Windows)
    .\venv\Scripts\activate
    # Activar entorno (Mac/Linux)
    source venv/bin/activate

### 2. Instalar dependencias

    pip install -r requirements.txt

### 3. Configurar variables de entorno (Secretos)
Crea un archivo llamado .env en la raíz del proyecto. Nunca subas este archivo a GitHub (ya está incluido en el .gitignore).


    APIFY_TOKEN=tu_token_gratuito_de_apify
    GEMINI_API_KEY=tu_api_key_gratuita_de_google_ai_studio
    URL_RESTAURANTE=url_de_google_maps_del_restaurante_a_auditar

### 4. Ejecutar el Pipeline de Datos
#### Paso 1: Extraer reseñas de Google Maps

    python extractor.py

#### Paso 2: Analizar los textos con Inteligencia Artificial (Batching)

    python analyzer.py

### 5. Lanzar el Panel de Control

    streamlit run app.py
El dashboard se abrirá automáticamente en tu navegador en http://localhost:8501.
