import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Indicadores Sanitarios",
    page_icon="🏥",
    layout="wide"
)

# Título principal
st.title("🏥 Dashboard de Indicadores Sanitarios y Gestión de Atención")
st.markdown("Tablero interactivo para el monitoreo de atenciones, tiempos de espera, inasistencias y satisfacción del usuario.")

# Cargar la base de datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("indicadores_sanitarios_ia.csv")
    return df

df = cargar_datos()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Búsqueda")

# Filtro por tipo de establecimiento
tipos_est = ['Todos'] + list(df['tipo_establecimiento'].unique())
tipo_sel = st.sidebar.selectbox("Seleccione Tipo de Establecimiento", tipos_est)

if tipo_sel != 'Todos':
    df_filtrado = df[df['tipo_establecimiento'] == tipo_sel]
else:
    df_filtrado = df.copy()

# Filtro por establecimiento específico
establecimientos = ['Todos'] + list(df_filtrado['establecimiento'].unique())
est_sel = st.sidebar.selectbox("Seleccione Establecimiento", establecimientos)

if est_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['establecimiento'] == est_sel]

# Filtro por especialidad
especialidades = ['Todas'] + list(df['especialidad'].unique())
esp_sel = st.sidebar.selectbox("Seleccione Especialidad", especialidades)

if esp_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['especialidad'] == esp_sel]

# --- TARJETAS DE MÉTRICAS PRINCIPALES ---
st.subheader("📊 Indicadores Globales")
col1, col2, col3, col4 = st.columns(4)

total_atenciones = int(df_filtrado['num_atenciones'].sum())
prom_espera = round(df_filtrado['tiempo_espera_min'].mean(), 1)
prom_inasistencia = round(df_filtrado['pct_inasistencia'].mean(), 1)
prom_satisfaccion = round(df_filtrado['satisfaccion_usuario'].mean(), 2)

col1.metric("Total Atenciones", f"{total_atenciones:,}")
col2.metric("Tiempo Promedio de Espera", f"{prom_espera} min")
col3.metric("Porcentaje Inasistencia", f"{prom_inasistencia}%")
col4.metric("Satisfacción Promedio", f"{prom_satisfaccion} / 5.0")

st.markdown("---")

# --- GRÁFICOS ANALÍTICOS ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Atenciones por Mes")
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                   'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    df_mes = df_filtrado.groupby('mes', as_index=False)['num_atenciones'].sum()
    df_mes['mes_num'] = df_mes['mes'].map({m: i for i, m in enumerate(orden_meses)})
    df_mes = df_mes.sort_values('mes_num')
    
    fig_mes = px.line(df_mes, x='mes', y='num_atenciones', markers=True,
                      labels={'mes': 'Mes', 'num_atenciones': 'Total Atenciones'},
                      color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_mes, use_container_width=True)

with col_g2:
    st.subheader("Satisfacción por Especialidad")
    df_esp = df_filtrado.groupby('especialidad', as_index=False)['satisfaccion_usuario'].mean()
    fig_esp = px.bar(df_esp, x='especialidad', y='satisfaccion_usuario',
                     labels={'especialidad': 'Especialidad', 'satisfaccion_usuario': 'Promedio Satisfacción'},
                     color='satisfaccion_usuario', color_continuous_scale='Blues')
    st.plotly_chart(fig_esp, use_container_width=True)

col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("Tiempo de Espera por Tipo de Establecimiento")
    df_tiempo = df_filtrado.groupby('tipo_establecimiento', as_index=False)['tiempo_espera_min'].mean()
    fig_tiempo = px.pie(df_tiempo, names='tipo_establecimiento', values='tiempo_espera_min',
                        hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_tiempo, use_container_width=True)

with col_g4:
    st.subheader("Porcentaje de Inasistencia por Establecimiento")
    df_inasis = df_filtrado.groupby('establecimiento', as_index=False)['pct_inasistencia'].mean()
    fig_inasis = px.bar(df_inasis, x='pct_inasistencia', y='establecimiento', orientation='h',
                        labels={'pct_inasistencia': '% Inasistencia', 'establecimiento': 'Establecimiento'},
                        color='pct_inasistencia', color_continuous_scale='Reds')
    st.plotly_chart(fig_inasis, use_container_width=True)

# --- TABLA DE DATOS FILTRADOS ---
st.markdown("---")
st.subheader("📋 Detalle de la Base de Datos Filtrada")
st.dataframe(df_filtrado, use_container_width=True)
