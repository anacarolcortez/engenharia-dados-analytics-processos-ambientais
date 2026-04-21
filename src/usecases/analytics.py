import re
import numpy as np
import pandas as pd
from src.infra.duckdb_client import DuckDBClient

class AnalyticsService:
    def __init__(self):
        self.db = DuckDBClient()

    def _tratar_df(self, df: pd.DataFrame):
        return df.replace({np.nan: None}).to_dict(orient="records")

    def processos_por_estado(self):
        query = f"""
            SELECT estado, COUNT(*) as total 
            FROM '{self.db.path}' 
            GROUP BY estado 
            ORDER BY total DESC
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def mapa_calor_severidade(self):
        query = f"""
            SELECT 
                estado,
                assunto_especifico,
                COUNT(*) as qtd_processos,
                CASE 
                    WHEN assunto_especifico IN ('DANO / REPARAÇÃO AMBIENTAL', 'DESAPROPRIAÇÃO') THEN 'ALTA'
                    WHEN assunto_especifico IN ('EXECUÇÃO DE DÍVIDA ATIVA', 'MULTA / INFRAÇÃO AMBIENTAL', 'MINERAÇÃO') THEN 'MÉDIA'
                    ELSE 'BAIXA'
                END as severidade
            FROM '{self.db.path}'
            GROUP BY ALL
            ORDER BY qtd_processos DESC
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def distribuicao_assuntos_detalhada(self, limit=20):
        query = f"""
            SELECT 
                assunto_especifico, 
                COUNT(*) as total,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
            FROM '{self.db.path}' 
            GROUP BY assunto_especifico
            ORDER BY total DESC
            LIMIT {limit}
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def processos_por_assunto_por_empresa(self, limit=50):
        query = f"""
            SELECT 
                assunto_especifico, 
                empresa_nome, 
                COUNT(*) as total 
            FROM '{self.db.path}' 
            WHERE empresa_nome IS NOT NULL
            GROUP BY ALL
            ORDER BY total DESC
            LIMIT {limit}
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def ranking_empresas_por_estado(self, limit=5):
        query = f"""
                SELECT 
                    estado, 
                    empresa_nome, 
                    COUNT(*) as total,
                    ROW_NUMBER() OVER (PARTITION BY estado ORDER BY COUNT(*) DESC) as ranking
                FROM '{self.db.path}'
                WHERE empresa_cnpj IS NOT NULL
                AND estado IS NOT NULL
                GROUP BY estado, empresa_nome
                QUALIFY ranking <= {limit}
                ORDER BY estado, ranking
            """
        df = self.db.query(query)
        return self._tratar_df(df)

    def estatisticas_tempo_por_categoria(self):
        query = f"""
            SELECT 
                assunto_especifico,
                AVG(tempo_processo_dias) as tempo_medio_dias,
                COUNT(*) as total_casos
            FROM '{self.db.path}'
            WHERE finalizado = True
            GROUP BY assunto_especifico
            HAVING total_casos > 5
            ORDER BY tempo_medio_dias DESC
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def buscar_processos_por_cnpj(self, cnpj_input: str):
        cnpj_numeros = re.sub(r'\D', '', cnpj_input)
        query = f"""
            SELECT 
                empresa_nome,
                numero_processo, 
                ano_distribuicao, 
                assunto,
                assunto_especifico, 
                estado, 
                status,
                qtd_partes_ativas,
                finalizado,
                tempo_processo_dias
            FROM '{self.db.path}'
            WHERE regexp_replace(empresa_cnpj, '[^0-9]', '', 'g') = '{cnpj_numeros}'
            ORDER BY ano_distribuicao DESC
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def resumo_financeiro_estimado(self):
        query = f"""
            SELECT 
                assunto_especifico,
                COUNT(*) as total_processos,
                CASE 
                    WHEN assunto_especifico = 'TRIBUTÁRIO (TCFA)' THEN 'Risco Tributário'
                    WHEN assunto_especifico = 'EXECUÇÃO DE DÍVIDA ATIVA' THEN 'Risco Patrimonial'
                    ELSE 'Risco Operacional'
                END as tipo_risco
            FROM '{self.db.path}'
            WHERE assunto_especifico IN ('TRIBUTÁRIO (TCFA)', 'EXECUÇÃO DE DÍVIDA ATIVA', 'MULTA / INFRAÇÃO AMBIENTAL')
            GROUP BY ALL
        """
        df = self.db.query(query)
        return self._tratar_df(df)
    
    def empresas_mais_processadas(self, limit=10):
        query = f"""
            SELECT 
                empresa_nome, 
                empresa_cnpj, 
                COUNT(*) as total
            FROM '{self.db.path}'
            WHERE empresa_nome IS NOT NULL
            GROUP BY ALL
            ORDER BY total DESC
            LIMIT {limit}
        """
        df = self.db.query(query)
        return self._tratar_df(df)

    def estatistica_percentual_finalizados(self):
        query = f"""
            SELECT 
                estado, 
                COUNT(*) as total_processos, 
                SUM(CASE WHEN finalizado THEN 1 ELSE 0 END) as processos_finalizados,
                ROUND(SUM(CASE WHEN finalizado THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentual_finalizados
            FROM '{self.db.path}'
            WHERE estado IS NOT NULL
            GROUP BY ALL
            ORDER BY percentual_finalizados DESC
        """
        df = self.db.query(query)
        return self._tratar_df(df)
    
    def estatisticas_tempo_processo(self):
        df = self.db.query(f"SELECT tempo_processo_dias FROM '{self.db.path}' WHERE finalizado = True")
        
        stats = {
            "media_dias": df['tempo_processo_dias'].mean(),
            "mediana_dias": df['tempo_processo_dias'].median(),
            "desvio_padrao": df['tempo_processo_dias'].std(),
            "p90_atraso": np.percentile(df['tempo_processo_dias'].dropna(), 90) if not df.empty else 0
        }
        
        return {k: (v if not (isinstance(v, float) and np.isnan(v)) else None) for k, v in stats.items()}
    
    def processos_por_ano(self):
        query = f"""
            SELECT ano_distribuicao, COUNT(*) as total 
            FROM '{self.db.path}' 
            GROUP BY ano_distribuicao 
            ORDER BY ano_distribuicao
        """
        df = self.db.query(query)
        return self._tratar_df(df)