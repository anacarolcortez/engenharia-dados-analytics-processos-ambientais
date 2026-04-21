from pydantic import BaseModel, Field
from typing import Optional

class Processo(BaseModel):
    numero_processo: str = Field(..., description="Número único do processo")
    assunto_codigo: Optional[int] = None
    assunto: Optional[str] = Field(None, description="Assunto raiz (ex: DIREITO AMBIENTAL)")
    assunto_especifico: Optional[str] = Field(None, description="Label jurídica detalhada (ex: TRIBUTÁRIO (TCFA))")
    jurisdicao: Optional[str] = None
    orgao_nome: Optional[str] = None
    classe_judicial: Optional[str] = None
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    status: Optional[str] = None
    ano_distribuicao: Optional[int] = None
    ano_ultima_movimentacao: Optional[int] = None
    tempo_processo_dias: Optional[float] = None
    finalizado: bool = False
    qtd_partes_ativas: int = 0
    tipo_parte_passiva: Optional[str] = None
    empresa_nome: Optional[str] = None
    empresa_cnpj: Optional[str] = None
    tem_advogado: bool = False
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "empresa_nome": "IBAMA",
                "numero_processo": "10092185920174013400",
                "ano_distribuicao": 2019,
                "assunto": "DIREITO AMBIENTAL",
                "assunto_especifico": "MULTA / INFRAÇÃO AMBIENTAL",
                "estado": "PA",
                "status": "EM ANDAMENTO",
                "qtd_partes_ativas": 3,
                "finalizado": False,
                "tempo_processo_dias": 450.5
            }
        }
    }

class ResumoDashboard(BaseModel):
    categoria: str
    total: int
    percentual: Optional[float] = None