import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.usecases.analytics import AnalyticsService

st.set_page_config(page_title="Analytics Processos Ambientais TRF1", layout="wide")
service = AnalyticsService()

def style_fig(fig):
    fig.update_layout(
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def render_kpis(stats):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Média de Dias", f"{stats['media_dias']:.0f}")
    col2.metric("Mediana", f"{stats['mediana_dias']:.0f}")
    col3.metric("Desvio Padrão", f"{stats['desvio_padrao']:.1f}")
    col4.metric("P90", f"{stats['p90_atraso']:.0f} dias")

def render_processos_por_estado():
    st.subheader("Processos por Estado")

    df = pd.DataFrame(service.processos_por_estado())

    fig = px.bar(
        df,
        x="estado",
        y="total",
        color="total",
        labels={"total": "Nº de Processos"},
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(style_fig(fig), width='stretch')

def render_tendencia_mensal():
    st.subheader("Tendência Mensal")

    df = pd.DataFrame(service.processos_por_ano())

    fig = px.line(
        df,
        x="ano_distribuicao",
        y="total",
        markers=True
    )

    st.plotly_chart(style_fig(fig), width='stretch')

def render_maiores_litigantes():
    st.subheader("Maiores Litigantes (Polo Passivo)")

    df = pd.DataFrame(service.empresas_mais_processadas(limit=5))

    fig = px.bar(
        df,
        x="total",
        y="empresa_nome",
        orientation="h",
        text="total",
        color="total",
        color_continuous_scale="Purp"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False
    )

    st.plotly_chart(style_fig(fig), width='stretch')

def render_ranking_por_estado():
    st.subheader("Top Litigantes por Estado")

    df = pd.DataFrame(service.ranking_empresas_por_estado(limit=5))

    estados = sorted(df["estado"].unique())
    estado = st.selectbox("Selecione o Estado:", estados)

    df_filtrado = df[df["estado"] == estado]

    if df_filtrado.empty:
        st.info("Nenhum dado disponível para este estado.")
        return

    fig = px.bar(
        df_filtrado,
        x="total",
        y="empresa_nome",
        orientation="h",
        text="total",
        color="total",
        labels={"empresa_nome": "Empresa", "total": "Qtd Processos"}
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False
    )

    st.plotly_chart(style_fig(fig), width='stretch')

    with st.expander("Ver tabela detalhada"):
        st.dataframe(df_filtrado, width='stretch')

def render_tempo_medio_por_estado():
    st.subheader("Tempo Médio por Estado")

    df = pd.DataFrame(service.tempo_medio_processo())

    fig = px.bar(
        df,
        x="estado",
        y="tempo_medio_dias",
        color="tempo_medio_dias",
        color_continuous_scale="YlOrRd"
    )

    fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')

    st.plotly_chart(style_fig(fig), use_container_width=True)

def render_percentual_finalizados():
    st.subheader("Eficiência por Estado - Finalizados (%)")
    
    df = pd.DataFrame(service.estatistica_percentual_finalizados())
    
    fig = px.bar(
        df,
        x="estado",
        y="percentual_finalizados",
        color="percentual_finalizados",
        text=df["percentual_finalizados"].apply(lambda x: f'{x:.1f}%'),
        labels={"percentual_finalizados": "Finalizado (%)", "estado": "Estado"},
        color_continuous_scale="Viridis"
    )
    
    fig.update_traces(textposition='outside')
    st.plotly_chart(style_fig(fig), use_container_width=True)

def render_processos_por_assunto():
    st.subheader("Principais Assuntos")
    
    df = pd.DataFrame(service.processos_por_assunto(limit=10))
    
    df = df.dropna(subset=['assunto'])
    df = df[df['assunto'].astype(str).str.lower() != "null"]
    df = df[df['assunto'].str.strip() != ""]

    fig = px.bar(
        df,
        x="total",
        y="assunto",
        orientation="h",
        text="total",
        color="total",
        labels={"total": "Qtd Processos", "assunto": "Assunto"},
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    fig.update_traces(textposition='outside')

    st.plotly_chart(style_fig(fig), use_container_width=True)

def load_stats():
    return service.estatisticas_tempo_processo()

def main():
    st.title("⚖️ 🌱 Processos Ambientais - TRF1 (Amazônia Legal)")
    st.divider()

    stats = load_stats()

    with st.container():
        st.subheader("Estatísticas Gerais")
        render_kpis(stats)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        render_processos_por_estado()

    with col2:
        render_tendencia_mensal()

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        render_maiores_litigantes()

    with col4:
        render_tempo_medio_por_estado()

    st.divider()

    render_ranking_por_estado()

    col5, col6 = st.columns(2)
    with col5:
        render_percentual_finalizados()
    with col6:
        render_processos_por_assunto()

    st.divider()

if __name__ == "__main__":
    main()