import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Configuración de la página web
st.set_page_config(page_title="Auditoría de Restaurantes", page_icon="🍽️", layout="wide")
st.title("🍽️ Auditoría de Restaurante")
st.markdown("Análisis automático de reseñas usando Inteligencia Artificial.")

# Cargar los datos desde SQLite
@st.cache_data(ttl=60) # Refresca los datos cada 60 segundos si hay cambios
def cargar_datos():
    try:
        # Nos conectamos a la base de datos SQLite
        conexion = sqlite3.connect("restaurantes.db")
        
        # Leemos SOLO las reseñas que la IA ha procesado con éxito
        query = "SELECT * FROM resenas WHERE sentimiento IS NOT NULL AND sentimiento != 'Error'"
        df = pd.read_sql_query(query, conexion)
        conexion.close()
        
        # Convertimos la columna fecha a formato datetime para el nuevo gráfico temporal
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
        return df
    except sqlite3.OperationalError:
        st.error("⚠️ No se encuentra la base de datos 'restaurantes.db'.")
        return pd.DataFrame()

df = cargar_datos()

if not df.empty:
    # Mostrar Métricas Clave (KPIs)
    st.header("Resumen General")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total de Reseñas Analizadas", value=len(df))
    with col2:
        nota_media = round(df["estrellas"].mean(), 1)
        st.metric(label="Nota Media (Estrellas)", value=f"{nota_media} / 5.0")
    with col3:
        positivos = len(df[df["sentimiento"] == "Positivo"])
        porcentaje = round((positivos / len(df)) * 100) if len(df) > 0 else 0
        st.metric(label="Satisfacción Global", value=f"{porcentaje}% Positivo")

    st.divider()

    # Zona de Gráficos
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        st.subheader("Sentimiento de los Clientes")
        fig_sentimiento = px.pie(df, names='sentimiento', color='sentimiento',
                                 color_discrete_map={'Positivo':'#00cc96', 'Negativo':'#ef553b', 'Neutral':'#636efa'})
        st.plotly_chart(fig_sentimiento, use_container_width=True)

    with col_grafico2:
        st.subheader("¿De qué hablan los clientes?")
        conteo_categorias = df.groupby(['categoria', 'sentimiento']).size().reset_index(name='Cantidad')
        fig_categorias = px.bar(conteo_categorias, x='categoria', y='Cantidad', color='sentimiento',
                                color_discrete_map={'Positivo':'#00cc96', 'Negativo':'#ef553b', 'Neutral':'#636efa'})
        st.plotly_chart(fig_categorias, use_container_width=True)

    st.divider()
    
    # Gráfico de Evolución Temporal
    if 'fecha' in df.columns and df['fecha'].notna().any():
        st.subheader("📈 Evolución Temporal (Nota Media por Mes)")
        # Agrupamos por mes y calculamos la media de estrellas
        df_temporal = df.copy()
        df_temporal['Mes'] = df_temporal['fecha'].dt.to_period('M').astype(str)
        evolucion = df_temporal.groupby('Mes')['estrellas'].mean().reset_index()
        
        # Ordenamos cronológicamente
        evolucion = evolucion.sort_values('Mes')
        
        fig_evolucion = px.line(evolucion, x='Mes', y='estrellas', markers=True, range_y=[1, 5])
        fig_evolucion.update_traces(line_color='#636efa', line_width=3, marker_size=8)
        st.plotly_chart(fig_evolucion, use_container_width=True)
        
        st.divider()

    # Tabla interactiva de Reseñas
    st.subheader("Buscador de Reseñas")
    
    filtro_categoria = st.selectbox("Filtrar por categoría:", ["Todas"] + df["categoria"].unique().tolist())
    
    if filtro_categoria != "Todas":
        df_filtrado = df[df["categoria"] == filtro_categoria]
    else:
        df_filtrado = df
        
    st.dataframe(df_filtrado[["fecha", "estrellas", "sentimiento", "categoria", "resumen", "texto"]], use_container_width=True)