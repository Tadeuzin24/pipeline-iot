import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


st.set_page_config(
    page_title="Dashboard IoT",
    page_icon="🌡️",
    layout="wide",
)

st.title("Pipeline de Dados IoT")
st.subheader("Análise de leituras de temperatura")
st.caption(
    "Dados históricos de sensores IoT armazenados no PostgreSQL."
)

password = os.getenv("DB_PASSWORD")

if not password:
    st.error(
        "A variável DB_PASSWORD não está definida. "
        "Configure a senha no PowerShell antes de executar o dashboard."
    )
    st.stop()

url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER", "iot_user"),
    password=password,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5433")),
    database=os.getenv("DB_NAME", "iot_data"),
)

engine = create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=60)
def load_data(query):
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)


try:
    resumo = load_data("""
        SELECT
            COUNT(*) AS total_leituras,
            ROUND(AVG(temp)::numeric, 2) AS temp_media,
            MIN(temp) AS temp_min,
            MAX(temp) AS temp_max
        FROM temperature_readings
    """)

    por_origem = load_data("""
        SELECT out_in, avg_temp, total_leituras
        FROM avg_temp_por_origem
        ORDER BY out_in
    """)

    por_hora = load_data("""
        SELECT hora, contagem
        FROM leituras_por_hora
        ORDER BY hora
    """)

    por_dia = load_data("""
        SELECT data, temp_max, temp_min
        FROM temp_max_min_por_dia
        ORDER BY data
    """)

except Exception as erro:
    st.error("Não foi possível carregar os dados do PostgreSQL.")
    st.code(str(erro))
    st.info(
        "Verifique se o contêiner postgres-iot está ativo "
        "e se as views SQL foram criadas."
    )
    st.stop()


dados = resumo.iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total de leituras",
    f"{int(dados['total_leituras']):,}".replace(",", "."),
)

col2.metric(
    "Temperatura média",
    f"{float(dados['temp_media']):.2f} °C",
)

col3.metric(
    "Faixa de temperatura",
    f"{int(dados['temp_min'])} a {int(dados['temp_max'])} °C",
)

st.divider()

st.header("1. Temperatura média por origem")

fig1 = px.bar(
    por_origem,
    x="out_in",
    y="avg_temp",
    text="avg_temp",
    hover_data=["total_leituras"],
    labels={
        "out_in": "Origem da leitura",
        "avg_temp": "Temperatura média (°C)",
        "total_leituras": "Quantidade de leituras",
    },
)

fig1.update_traces(
    texttemplate="%{text:.2f} °C",
    textposition="outside",
)

st.plotly_chart(fig1, use_container_width=True)

st.header("2. Quantidade de leituras por hora")

fig2 = px.line(
    por_hora,
    x="hora",
    y="contagem",
    markers=True,
    labels={
        "hora": "Hora do dia",
        "contagem": "Quantidade de leituras",
    },
)

fig2.update_xaxes(dtick=1)
st.plotly_chart(fig2, use_container_width=True)

st.header("3. Temperaturas máxima e mínima por dia")

fig3 = px.line(
    por_dia,
    x="data",
    y=["temp_max", "temp_min"],
    labels={
        "data": "Data",
        "value": "Temperatura (°C)",
        "variable": "Métrica",
    },
)

st.plotly_chart(fig3, use_container_width=True)

st.caption(
    "Projeto acadêmico de IoT e Big Data. "
    "As visualizações utilizam dados históricos do arquivo CSV."
)

engine.dispose()
