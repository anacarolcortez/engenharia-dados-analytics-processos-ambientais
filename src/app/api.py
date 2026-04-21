from typing import List
from fastapi import FastAPI, HTTPException, Depends
from src.domain.schemas import Processo 
from src.usecases.analytics import AnalyticsService

app = FastAPI(
    title="Analytics Processos Ambientais - TRF1",
    description="API de análise de dados jurídicos ambientais com foco em BI e Risco"
)

def get_analytics_service():
    return AnalyticsService()


@app.get("/processos/por-estado")
def get_processos_por_estado(service: AnalyticsService = Depends(get_analytics_service)):
    return service.processos_por_estado()

@app.get("/processos/mapa-severidade")
def get_mapa_severidade(service: AnalyticsService = Depends(get_analytics_service)):
    """Retorna dados para o Mapa de Calor (Estado vs Severidade)"""
    return service.mapa_calor_severidade()

@app.get("/processos/por-assunto-detalhado")
def get_assuntos_detalhados(limit: int = 20, service: AnalyticsService = Depends(get_analytics_service)):
    """Usa as novas labels jurídicas esmiuçadas"""
    return service.distribuicao_assuntos_detalhada(limit)

@app.get("/processos/financeiro-estimado")
def get_resumo_financeiro(service: AnalyticsService = Depends(get_analytics_service)):
    """Retorna visão de Risco Tributário vs Patrimonial"""
    return service.resumo_financeiro_estimado()

@app.get("/empresas/ranking")
def get_ranking_empresas(limit: int = 10, service: AnalyticsService = Depends(get_analytics_service)):
    return service.empresas_mais_processadas(limit)

@app.get("/empresas/ranking-por-estado")
def get_ranking_empresas_por_estado(limit: int = 5, service: AnalyticsService = Depends(get_analytics_service)):
    return service.ranking_empresas_por_estado(limit)

@app.get("/estatisticas/tempo-por-categoria")
def get_tempo_por_categoria(service: AnalyticsService = Depends(get_analytics_service)):
    """Novo: Mostra quais temas ambientais demoram mais no judiciário"""
    return service.estatisticas_tempo_por_categoria()

@app.get("/estatisticas/percentual-finalizados")
def get_estatistica_percentual_finalizados(service: AnalyticsService = Depends(get_analytics_service)):
    return service.estatistica_percentual_finalizados()

@app.get("/processos/cnpj/{cnpj}")
def get_by_cnpj(cnpj: str, service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.buscar_processos_por_cnpj(cnpj)
    if not dados:
        raise HTTPException(status_code=404, detail="Nenhum processo encontrado para este CNPJ")
    return dados