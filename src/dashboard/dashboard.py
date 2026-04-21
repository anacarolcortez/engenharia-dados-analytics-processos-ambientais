# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# import streamlit as st
# import pandas as pd
# import plotly.express as px

# from src.usecases.analytics import AnalyticsService

# st.set_page_config(page_title="Analytics Processos Ambientais TRF1", layout="wide")
# service = AnalyticsService()

# def style_fig(fig):
#     fig.update_layout(
#         template="plotly_white",
#         height=380,
#         margin=dict(l=10, r=10, t=40, b=10)
#     )
#     return fig

# def render_kpis(stats):
#     col1, col2, col3, col4 = st.columns(4)

#     col1.metric("Média de Dias", f"{stats['media_dias']:.0f}")
#     col2.metric("Mediana", f"{stats['mediana_dias']:.0f}")
#     col3.metric("Desvio Padrão", f"{stats['desvio_padrao']:.1f}")
#     col4.metric("P90", f"{stats['p90_atraso']:.0f} dias")

# def render_processos_por_estado():
#     st.subheader("Processos por Estado")

#     df = pd.DataFrame(service.processos_por_estado())

#     fig = px.bar(
#         df,
#         x="estado",
#         y="total",
#         color="total",
#         labels={"total": "Nº de Processos"},
#         color_continuous_scale="Viridis"
#     )

#     st.plotly_chart(style_fig(fig), width='stretch')

# def render_tendencia_mensal():
#     st.subheader("Tendência Mensal")

#     df = pd.DataFrame(service.processos_por_ano())

#     fig = px.line(
#         df,
#         x="ano_distribuicao",
#         y="total",
#         markers=True
#     )

#     st.plotly_chart(style_fig(fig), width='stretch')

# def render_maiores_litigantes():
#     st.subheader("Maiores Litigantes (Polo Passivo)")

#     df = pd.DataFrame(service.empresas_mais_processadas(limit=10))

#     fig = px.bar(
#         df,
#         x="total",
#         y="empresa_nome",
#         orientation="h",
#         text="total",
#         color="total",
#         color_continuous_scale="Purp"
#     )

#     fig.update_layout(
#         yaxis={"categoryorder": "total ascending"},
#         coloraxis_showscale=False
#     )

#     st.plotly_chart(style_fig(fig), width='stretch')

# def render_ranking_por_estado():
#     st.subheader("Top Litigantes por Estado")

#     df = pd.DataFrame(service.ranking_empresas_por_estado(limit=10))

#     estados = sorted(df["estado"].unique())
#     estado = st.selectbox("Selecione o Estado:", estados)

#     df_filtrado = df[df["estado"] == estado]

#     if df_filtrado.empty:
#         st.info("Nenhum dado disponível para este estado.")
#         return

#     fig = px.bar(
#         df_filtrado,
#         x="total",
#         y="empresa_nome",
#         orientation="h",
#         text="total",
#         color="total",
#         labels={"empresa_nome": "Empresa", "total": "Qtd Processos"}
#     )

#     fig.update_layout(
#         yaxis={"categoryorder": "total ascending"},
#         showlegend=False
#     )

#     st.plotly_chart(style_fig(fig), width='stretch')

#     with st.expander("Ver tabela detalhada"):
#         st.dataframe(df_filtrado, width='stretch')

# def render_tempo_medio_por_estado():
#     st.subheader("Tempo Médio por Estado")

#     df = pd.DataFrame(service.tempo_medio_processo())

#     fig = px.bar(
#         df,
#         x="estado",
#         y="tempo_medio_dias",
#         color="tempo_medio_dias",
#         color_continuous_scale="YlOrRd"
#     )

#     fig.update_traces(texttemplate='%{y:.0f}', textposition='outside')

#     st.plotly_chart(style_fig(fig), use_container_width=True)

# def render_percentual_finalizados():
#     st.subheader("Eficiência por Estado - Finalizados (%)")
    
#     df = pd.DataFrame(service.estatistica_percentual_finalizados())
    
#     fig = px.bar(
#         df,
#         x="estado",
#         y="percentual_finalizados",
#         color="percentual_finalizados",
#         text=df["percentual_finalizados"].apply(lambda x: f'{x:.1f}%'),
#         labels={"percentual_finalizados": "Finalizado (%)", "estado": "Estado"},
#         color_continuous_scale="Viridis"
#     )
    
#     fig.update_traces(textposition='outside')
#     st.plotly_chart(style_fig(fig), use_container_width=True)

# def render_processos_por_assunto():
#     st.subheader("Principais Assuntos")
    
#     df = pd.DataFrame(service.processos_por_assunto(limit=10))
    
#     df = df.dropna(subset=['assunto'])
#     df = df[df['assunto'].astype(str).str.lower() != "null"]
#     df = df[df['assunto'].str.strip() != ""]

#     df = df.sort_values("total", ascending=True)

#     fig = px.bar(
#         df,
#         x="total",
#         y="assunto",
#         orientation="h",
#         text="total",
#         color="total",
#         labels={
#             "total": "Qtd Processos",
#             "assunto": "Assunto"
#         },
#         color_continuous_scale="Blues"
#     )

#     fig.update_traces(textposition="outside")
#     fig.update_layout(
#         yaxis={'categoryorder': 'total ascending'},
#         xaxis_title="Qtd Processos",
#         yaxis_title="Assunto",
#         margin=dict(l=0, r=20, t=30, b=0)
#     )

#     st.plotly_chart(fig, use_container_width=True)

# def render_processos_por_assunto_empresa():
#     st.subheader("Assuntos por Empresa")
    
#     df = pd.DataFrame(service.processos_por_assunto_por_empresa(limit=50))

#     df = df.dropna(subset=['assunto', 'empresa_nome'])
#     df = df[df['assunto'].str.strip() != ""]
#     df = df[df['empresa_nome'].str.strip() != ""]

#     top_n = st.slider("Qtd de empresas", 3, 15, 5)

#     top_empresas = (
#         df.groupby("empresa_nome")["total"]
#         .sum()
#         .nlargest(top_n)
#         .index
#     )
#     df = df[df["empresa_nome"].isin(top_empresas)]

#     ordem = (
#         df.groupby("assunto")["total"]
#         .sum()
#         .sort_values()
#         .index
#     )

#     fig = px.bar(
#         df,
#         x="total",
#         y="assunto",
#         color="empresa_nome",
#         orientation="h",
#         labels={
#             "total": "Qtd Processos",
#             "assunto": "Assunto",
#             "empresa_nome": "Empresa"
#         }
#     )

#     fig.update_layout(
#         yaxis={
#             'categoryorder': 'array',
#             'categoryarray': ordem
#         },
#         xaxis_title="Qtd Processos",
#         yaxis_title="Assunto",
#         legend_title="Empresa",
#         margin=dict(l=0, r=20, t=30, b=0)
#     )

#     st.plotly_chart(fig, use_container_width=True)

# def load_stats():
#     return service.estatisticas_tempo_processo()

# def main():
#     st.title("⚖️ 🌱 Processos Ambientais - TRF1 (Amazônia Legal)")
#     st.divider()

#     stats = load_stats()

#     with st.container():
#         st.subheader("Estatísticas Gerais")
#         render_kpis(stats)

#     st.divider()

#     col1, col2 = st.columns(2)

#     with col1:
#         render_processos_por_estado()

#     with col2:
#         render_tendencia_mensal()

#     st.divider()

#     col3, col4 = st.columns(2)

#     with col3:
#         render_maiores_litigantes()

#     with col4:
#         render_tempo_medio_por_estado()

#     st.divider()

#     render_ranking_por_estado()

#     col5, col6 = st.columns(2)
#     with col5:
#         render_percentual_finalizados()
#     with col6:
#         render_processos_por_assunto()

#     st.divider()

#     render_processos_por_assunto_empresa()

# if __name__ == "__main__":
#     main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.usecases.analytics import AnalyticsService

st.set_page_config(
    page_title="Processos Ambientais na Amazônia Legal - TRF1", 
    layout="wide",
    page_icon="🌱"
)

service = AnalyticsService()

def style_fig(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

def render_kpis():
    stats = service.estatisticas_tempo_processo()
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Média de Dias", f"{stats['media_dias']:.0f}")
    col2.metric("Mediana", f"{stats['mediana_dias']:.0f}")
    col3.metric("Desvio Padrão", f"{stats['desvio_padrao']:.1f}")
    col4.metric("P90 (Atraso Crítico)", f"{stats['p90_atraso']:.0f} dias")

def render_mapa_severidade():
    st.subheader("🔥 Severidade por Estado")
    df = pd.DataFrame(service.mapa_calor_severidade())
    if not df.empty:
        fig = px.bar(
            df, x="estado", y="qtd_processos", color="severidade",
            color_discrete_map={'ALTA': '#EF553B', 'MÉDIA': '#FECB52', 'BAIXA': '#636EFA'},
            barmode="stack", labels={"qtd_processos": "Processos"}
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_tendencia_anual():
    st.subheader("📈 Tendência de Distribuição")
    df = pd.DataFrame(service.processos_por_ano())
    if not df.empty:
        fig = px.line(df, x="ano_distribuicao", y="total", markers=True)
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_assuntos_detalhados():
    st.subheader("🎯 Assuntos Detalhados")
    df = pd.DataFrame(service.distribuicao_assuntos_detalhada(limit=15))
    if not df.empty:
        fig = px.bar(
            df, x="total", y="assunto_especifico", orientation="h",
            text=df["percentual"].apply(lambda x: f'{x}%'),
            color="total", color_continuous_scale="Blues"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_risco_financeiro():
    st.subheader("💰 Divisão de Riscos")
    df = pd.DataFrame(service.resumo_financeiro_estimado())
    if not df.empty:
        fig = px.pie(df, values='total_processos', names='assunto_especifico', hole=0.4)
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_maiores_litigantes():
    st.subheader("🏢 Maiores Litigantes (Geral)")
    df = pd.DataFrame(service.empresas_mais_processadas(limit=10))
    if not df.empty:
        fig = px.bar(
            df, x="total", y="empresa_nome", orientation="h",
            color="total", color_continuous_scale="Purp"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_ranking_por_estado():
    st.subheader("📍 Top Litigantes por Estado")
    df = pd.DataFrame(service.ranking_empresas_por_estado(limit=10))
    if not df.empty:
        estado = st.selectbox("Selecione o Estado:", sorted(df["estado"].unique()))
        df_filtrado = df[df["estado"] == estado]
        fig = px.bar(df_filtrado, x="total", y="empresa_nome", orientation="h", color="total")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_percentual_finalizados():
    st.subheader("✅ Taxa de Encerramento por Estado")
    df = pd.DataFrame(service.estatistica_percentual_finalizados())
    if not df.empty:
        fig = px.bar(
            df, x="estado", y="percentual_finalizados", color="percentual_finalizados",
            text=df["percentual_finalizados"].apply(lambda x: f'{x:.1f}%'),
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_tempo_por_categoria():
    st.subheader("⏳ Gargalos por Assunto (Tempo Médio)")
    df = pd.DataFrame(service.estatisticas_tempo_por_categoria())
    if not df.empty:
        fig = px.scatter(
            df, x="tempo_medio_dias", y="assunto_especifico", size="total_casos",
            color="tempo_medio_dias", color_continuous_scale="Reds"
        )
        st.plotly_chart(style_fig(fig), use_container_width=True)

def render_assunto_por_empresa():
    st.subheader("🔍 Assuntos Detalhados por Empresa")
    df = pd.DataFrame(service.processos_por_assunto_por_empresa(limit=50))
    if not df.empty:
        top_n = st.slider("Quantidade de Empresas", 3, 15, 5)
        top_empresas = df.groupby("empresa_nome")["total"].sum().nlargest(top_n).index
        df_plot = df[df["empresa_nome"].isin(top_empresas)]
        
        fig = px.bar(df_plot, x="total", y="assunto_especifico", color="empresa_nome", orientation="h")
        st.plotly_chart(style_fig(fig, height=500), use_container_width=True)

def main():
    st.title("⚖️ 🌱 Processos Ambientais TRF1")
    st.caption("Dashboard de Inteligência Jurídica e Gestão de Risco Ambiental")
    
    render_kpis()
    st.divider()

    col1, col2 = st.columns(2)
    with col1: render_mapa_severidade()
    with col2: render_tendencia_anual()

    st.divider()

    col3, col4 = st.columns([2, 1])
    with col3: render_assuntos_detalhados()
    with col4: render_risco_financeiro()

    st.divider()

    col5, col6 = st.columns(2)
    with col5: render_maiores_litigantes()
    with col6: render_tempo_por_categoria()

    st.divider()

    render_ranking_por_estado()
    
    st.divider()

    col7, col8 = st.columns([1, 1])
    with col7: render_percentual_finalizados()
    with col8: st.info("ℹ️ As taxas de encerramento ajudam a identificar onde os processos estão travados na fase de execução.")

    st.divider()
    render_assunto_por_empresa()

if __name__ == "__main__":
    main()