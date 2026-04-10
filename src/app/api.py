from typing import List
from fastapi import FastAPI, HTTPException, Depends
from src.domain.schemas import Processo
from src.usecases.analytics import AnalyticsService

app = FastAPI(title="Analytics Processos Ambientais - TRF1")

def get_analytics_service():
    return AnalyticsService()

@app.get("/processos/por-estado")
def get_processos_por_estado(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.processos_por_estado()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/processos/por-ano")
def get_processos_por_ano(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.processos_por_ano()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/processos/por-assunto")
def get_processos_por_assunto(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.processos_por_assunto()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/processos/cnpj/{cnpj}", response_model=List[Processo])
def get_by_cnpj(cnpj: str, service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.buscar_processos_por_cnpj(cnpj)
    if not dados:
        raise HTTPException(status_code=404, detail="CNPJ não encontrado na base")
    return dados

@app.get("/processos/tempo-medio")
def get_tempo_medio(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.tempo_medio_processo()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/processos/cnpj/{cnpj}", response_model=List[Processo])
def get_by_cnpj(cnpj: str, service: AnalyticsService = Depends(get_analytics_service)):
    service = AnalyticsService()
    dados = service.buscar_processos_por_cnpj(cnpj)
    if not dados:
        raise HTTPException(status_code=404, detail="Nenhum processo encontrado para este CNPJ")  
    return dados

@app.get("/empresas/ranking")
def get_ranking_empresas(limit: int = 10, service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.empresas_mais_processadas(limit)
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/empresas/ranking-por-estado")
def get_ranking_empresas_por_estado(limit: int = 10, service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.ranking_empresas_por_estado(limit)
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/estatisticas/tempo-processo")
def get_estatisticas_tempo_processo(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.estatisticas_tempo_processo()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados

@app.get("/estatisticas/percentual-finalizados")
def get_estatistica_percentual_finalizados(service: AnalyticsService = Depends(get_analytics_service)):
    dados = service.estatistica_percentual_finalizados()
    if not dados:
        raise HTTPException(status_code=404, detail="Dados não encontrados")
    return dados