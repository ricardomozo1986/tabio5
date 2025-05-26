
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout='wide', page_title='Demo Ejecutiva Predial')
st.title("🌐 Plataforma Ejecutiva de Análisis Predial")

st.markdown("""
Esta plataforma ejecutiva permite visualizar información clave del estado tributario predial del municipio,
identificar oportunidades de recaudo, y orientar decisiones estratégicas de gestión fiscal.
""")

# --- Cargar archivo ---
uploaded_file = st.file_uploader("Carga la base de datos predial (.xlsx)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- Normalizar columnas ---
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("á", "a")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
    )

    # Indicadores clave
    st.markdown("## 📊 Indicadores Clave del Municipio")
    total_predios = len(df)
    total_avaluo = df['avaluo_catastral'].sum()
    total_impuesto = df['valor_impuesto_a_pagar'].sum()
    total_recaudo = df['recaudo_predial'].sum()
    cumplimiento = df['pago_impuesto_predial'].str.lower().eq('si').mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total predios", f"{total_predios:,}")
    col2.metric("Impuesto Total", f"${total_impuesto:,.0f}")
    col3.metric("Recaudo Total", f"${total_recaudo:,.0f}")

    col4, col5 = st.columns(2)
    col4.metric("Avalúo Total", f"${total_avaluo:,.0f}")
    col5.metric("Cumplimiento (%)", f"{cumplimiento:.2f}%")

    # Filtros básicos
    veredas = ['Todas'] + sorted(df['vereda'].dropna().unique().tolist())
    filtro_vereda = st.selectbox("Filtrar por vereda", veredas)

    if filtro_vereda != 'Todas':
        df = df[df['vereda'] == filtro_vereda]

    # Mapa general: cumplimiento
    st.markdown("## 🗺️ Mapa General de Cumplimiento Predial")
    df['cumplimiento'] = df['pago_impuesto_predial'].str.lower().eq('si')
    mapa = folium.Map(location=[df['latitud'].mean(), df['longitud'].mean()], zoom_start=12)

    for _, row in df.iterrows():
        color = 'green' if row['cumplimiento'] else 'red'
        folium.CircleMarker(
            location=[row['latitud'], row['longitud']],
            radius=5,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=(f"Predio IGAC: {row['codigo_igac']}<br>"
                   f"Vereda: {row['vereda']}<br>"
                   f"Avalúo: ${row['avaluo_catastral']:,.0f}<br>"
                   f"Impuesto: ${row['valor_impuesto_a_pagar']:,.0f}<br>"
                   f"Pago: {'Sí' if row['cumplimiento'] else 'No'}")
        ).add_to(mapa)

    st_folium(mapa, width=700, height=500)

    # Recomendaciones
    st.markdown("## ✅ Recomendaciones Estratégicas")
    st.markdown("""
    - Fortalecer campañas de recaudo en veredas con baja tasa de cumplimiento.
    - Priorizar visitas técnicas a predios con avalúo alto sin área construida registrada.
    - Establecer acuerdos de pago flexibles con los 50 predios de mayor deuda.
    """)
