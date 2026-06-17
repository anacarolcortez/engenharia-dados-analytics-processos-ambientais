from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

MAPEAMENTO_SETORES = {
    # 01 a 03: Agropecuária, Agricultura e Pesca
    "01": "Agropecuária e Agricultura", 
    "02": "Agropecuária e Agricultura", 
    "03": "Agropecuária e Agricultura",
    
    # 05 a 33: Indústria (Extrativa e Transformação)
    "05": "Indústria Extrativa", 
    "06": "Indústria Extrativa", 
    "07": "Indústria Extrativa", 
    "08": "Indústria Extrativa", 
    "09": "Indústria Extrativa",
    **{f"{i:02d}": "Indústria de Transformação" for i in range(10, 34)},
    
    "35": "Energia, Gás e Utilidades",
    "36": "Saneamento e Meio Ambiente", 
    "37": "Saneamento e Meio Ambiente", 
    "38": "Saneamento e Meio Ambiente", 
    "39": "Saneamento e Meio Ambiente",
    "41": "Construção Civil", "42": "Construção Civil", 
    "43": "Construção Civil",
    "45": "Comércio Automotivo",
    "46": "Comércio Atacadista",
    "47": "Comércio Varejista",
    "49": "Transporte e Logística", 
    "50": "Transporte e Logística", 
    "51": "Transporte e Logística", 
    "52": "Transporte e Logística", 
    "53": "Serviços Postais e Entrega",
    "55": "Hotéis e Alojamento", 
    "56": "Restaurantes e Alimentação",
    "58": "Mídia e Edição", 
    "59": "Produção Audiovisual e Música", 
    "60": "Telecomunicações e rádio/TV", 
    "61": "Telecomunicações e rádio/TV",
    "62": "Tecnologia da Informação (TI)", 
    "63": "Serviços de Informação e TI",
    "64": "Bancos e Serviços Financeiros", 
    "65": "Seguros e Previdência", 
    "66": "Serviços Financeiros Auxiliares",
    "68": "Mercado Imobiliário",
    "69": "Serviços Jurídicos e Contabilidade",
    "70": "Consultoria e Gestão Empresarial",
    "71": "Arquitetura e Engenharia",
    "72": "Pesquisa e Desenvolvimento",
    "73": "Publicidade e Pesquisa de Mercado",
    "74": "Design e Serviços Profissionais",
    "75": "Serviços Veterinários",
    "77": "Aluguel de Bens e Locação",
    "78": "Recursos Humanos e Seleção",
    "79": "Turismo e Agências de Viagem",
    "80": "Segurança e Investigação",
    "81": "Serviços para Edifícios e Paisagismo",
    "82": "Serviços de Escritório e Apoio Administrativo",
    "84": "Administração Pública e Defesa",
    "85": "Educação e Ensino",
    "86": "Saúde Humana e Hospitais", 
    "87": "Assistência Social com Alojamento", 
    "88": "Serviços Sociais e ONGs",
    "90": "Artes, Cultura e Entretenimento", 
    "91": "Proteção Ambiental", 
    "92": "Casas de Apostas e Jogos", 
    "93": "Esportes e Lazer",    
    "94": "Organizações Sociais e Sindicatos",
    "95": "Manutenção e Reparação de Bens",
    "96": "Serviços Pessoais (Beleza, Lavanderia, etc.)",
    "97": "Serviços Domésticos", 
    "99": "Organizações Internacionais"
}

def _traduzir_setor_cnae(series_cnae: pd.Series) -> pd.Series:
    cnae_limpo = (
        series_cnae.astype(str)
        .str.replace(r"\D", "", regex=True)
        .str.zfill(7)
    )

    divisao_cnae = cnae_limpo.str[:2]

    return divisao_cnae.map(MAPEAMENTO_SETORES).fillna("SETOR NÃO IDENTIFICADO")

def _limpar_e_converter_vector(series):
    if series.dtype == "object":
        series = (
            series.astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
    return pd.to_numeric(series, errors="coerce").fillna(0.0)


def _classificar_porte_vetorizado(df: pd.DataFrame) -> pd.Series:
    if "natureza_juridica" not in df.columns:
        return pd.Series("OUTROS", index=df.index)

    nj = (
        df["natureza_juridica"]
        .astype(str)
        .str.replace("-", "", regex=False)
        .str.replace(".", "", regex=False)
    )
    nome = df["empresa_polo_passivo_nome"].astype(str).str.upper()
    porte = pd.to_numeric(df["porte"], errors="coerce").fillna(-1).astype(int)
    capital = _limpar_e_converter_vector(df["capital_social"])

    is_sa = (
        nj.str.startswith("204")
        | nj.str.startswith("205")
        | nome.str.contains("S.A.", regex=False)
        | nome.str.contains("S/A", regex=False)
    )

    condicoes = [
        nj.str.startswith("1"),  # 1. Setor Público
        (capital > 50_000_000)
        | nj.str.startswith("204")
        | nj.str.startswith("205"),  # 2. Gigante
        is_sa
        | (capital > 5_000_000)
        | (porte == 5),  # 3. Grande Empresa
        (capital > 1_000_000),  # 4. Média Empresa
        (porte == 1)
        | (porte == 3)
        | (capital <= 1_000_000),  # 5. PME
    ]

    resultados = [
        "SETOR PUBLICO",
        "GIGANTE / MULTINACIONAL",
        "GRANDE EMPRESA",
        "MÉDIA EMPRESA",
        "PME / PEQUENO NEGÓCIO",
    ]

    return np.select(condicoes, resultados, default="OUTROS")

def _transformar_com_receita_e_cnae(
    df_origem, path_rf_empresa: str, path_rf_estab: str, manter_detalhes=True
) -> pd.DataFrame:
    df_origem["cnpj_base"] = (
        df_origem["empresa_polo_passivo_cnpj"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .str[:8]
    )

    con = duckdb.connect()

    query = f"""
        SELECT 
            emp.cnpj_base,
            emp.natureza_juridica,
            emp.capital_social,
            emp.porte,
            estab.cnae_fiscal_principal,
        FROM '{path_rf_empresa}' emp
        LEFT JOIN '{path_rf_estab}' estab 
            ON emp.cnpj_base = estab.cnpj_basico
        WHERE emp.cnpj_base IN (SELECT cnpj_base FROM df_origem)
    """

    df_rf_consolidado = con.execute(query).df()

    df_rf_consolidado["cnpj_base"] = (df_rf_consolidado["cnpj_base"].astype(str).str.zfill(8))
    df_rf_consolidado = df_rf_consolidado.drop_duplicates(subset=["cnpj_base"])

    df_merge = pd.merge(df_origem, df_rf_consolidado, on="cnpj_base", how="left")
    df_merge["categoria"] = _classificar_porte_vetorizado(df_merge)
    df_merge["setor_atuacao"] = _traduzir_setor_cnae(df_merge["cnae_fiscal_principal"])

    if not manter_detalhes:
        colunas_remover = ["natureza_juridica", "capital_social", "porte"]
        df_merge = df_merge.drop(columns=colunas_remover, errors="ignore")

    return df_merge


def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    base_path_processos = BASE_DIR / "data" / "silver" / "processos.parquet"
    base_path_rf_empresa = (BASE_DIR / "data" / "bronze" / "base_receita_consolidada.parquet")
    base_path_rf_estab = (BASE_DIR / "data" / "bronze" / "estabelecimentos_consolidado.parquet")
    processed_path_processos = (BASE_DIR / "data" / "gold" / "detalhe_processos.parquet")


    df_proc = pd.read_parquet(str(base_path_processos))
    df_processos_gold = _transformar_com_receita_e_cnae(
        df_proc,
        str(base_path_rf_empresa),
        str(base_path_rf_estab),
        manter_detalhes=False,
    )
    df_processos_gold.to_parquet(str(processed_path_processos))

    return df_processos_gold