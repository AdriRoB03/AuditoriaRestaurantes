import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Auditoría de Restaurantes", page_icon="🍽️", layout="wide")
st.title("🍽️ Panel de Inteligencia de Negocio")
st.markdown("Análisis automático de reseñas usando Inteligencia Artificial.")

# 2. Cargar los datos
@st.cache_data # Esto hace que la web cargue más rápido
def cargar_datos():
    try:
        # Leemos el archivo que generó la IA
        df = pd.read_csv("analyzed_reviews.csv")
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encuentra el archivo 'analyzed_reviews.csv'. Ejecuta primero la Fase 2 y 3.")
        return pd.DataFrame()

df = cargar_datos()

if not df.empty:
    # 3. Mostrar Métricas Clave (KPIs) en la parte superior
    st.header("Resumen General")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total de Reseñas Analizadas", value=len(df))
    with col2:
        nota_media = round(df["estrellas"].mean(), 1)
        st.metric(label="Nota Media (Estrellas)", value=f"{nota_media} / 5.0")
    with col3:
        positivos = len(df[df["Sentimiento"] == "Positivo"])
        porcentaje = round((positivos / len(df)) * 100)
        st.metric(label="Satisfacción Global", value=f"{porcentaje}% Positivo")

    st.divider() # Línea separadora

    # 4. Zona de Gráficos (Dividimos la pantalla en 2 columnas)
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("Sentimiento de los Clientes")
        # Gráfico de tarta con Plotly
        fig_sentimiento = px.pie(df, names='Sentimiento', color='Sentimiento',
                                 color_discrete_map={'Positivo':'#00cc96', 'Negativo':'#ef553b', 'Neutral':'#636efa'})
        st.plotly_chart(fig_sentimiento, use_container_width=True)

    with col_grafico2:
        st.subheader("¿De qué hablan los clientes?")
        # Gráfico de barras contando las categorías
        conteo_categorias = df.groupby(['Categoria', 'Sentimiento']).size().reset_index(name='Cantidad')
        fig_categorias = px.bar(conteo_categorias, x='Categoria', y='Cantidad', color='Sentimiento',
                                color_discrete_map={'Positivo':'#00cc96', 'Negativo':'#ef553b', 'Neutral':'#636efa'})
        st.plotly_chart(fig_categorias, use_container_width=True)

    st.divider()

    # 5. Tabla interactiva de Reseñas
    st.subheader("Buscador de Reseñas")
    
    # Filtro interactivo
    filtro_categoria = st.selectbox("Filtrar por categoría:", ["Todas"] + df["Categoria"].unique().tolist())
    
    if filtro_categoria != "Todas":
        df_filtrado = df[df["Categoria"] == filtro_categoria]
    else:
        df_filtrado = df
        
    # Mostramos las columnas más importantes
    st.dataframe(df_filtrado[["estrellas", "Sentimiento", "Categoria", "Resumen", "texto"]], use_container_width=True)