from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

MAPEAMENTO_SETORES = {
    # 01 a 03: Agropecuária, Agricultura e Pesca
    "01": "Agropecuária e Agricultura",
    "02": "Agropecuária e Agricultura",
    "03": "Agropecuária e Agricultura",

    # 05 a 09: Indústria Extrativa
    "05": "Indústria Extrativa",
    "06": "Indústria Extrativa",
    "07": "Indústria Extrativa",
    "08": "Indústria Extrativa",
    "09": "Indústria Extrativa",

    # 10 a 33: Indústria de Transformação (Expandido)
    "10": "Indústria de Transformação",
    "11": "Indústria de Transformação",
    "12": "Indústria de Transformação",
    "13": "Indústria de Transformação",
    "14": "Indústria de Transformação",
    "15": "Indústria de Transformação",
    "16": "Indústria de Transformação",
    "17": "Indústria de Transformação",
    "18": "Indústria de Transformação",
    "19": "Indústria de Transformação",
    "20": "Indústria de Transformação",
    "21": "Indústria de Transformação",
    "22": "Indústria de Transformação",
    "23": "Indústria de Transformação",
    "24": "Indústria de Transformação",
    "25": "Indústria de Transformação",
    "26": "Indústria de Transformação",
    "27": "Indústria de Transformação",
    "28": "Indústria de Transformação",
    "29": "Indústria de Transformação",
    "30": "Indústria de Transformação",
    "31": "Indústria de Transformação",
    "32": "Indústria de Transformação",
    "33": "Indústria de Transformação",

    # Demais Setores e Serviços
    "35": "Energia, Gás e Utilidades",
    "36": "Saneamento e Meio Ambiente",
    "37": "Saneamento e Meio Ambiente",
    "38": "Saneamento e Meio Ambiente",
    "39": "Saneamento e Meio Ambiente",
    "41": "Construção Civil",
    "42": "Construção Civil",
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
    "99": "Organizações Internacionais",
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
        (capital > 50_000_000) | nj.str.startswith("204") | nj.str.startswith("205"),  # 2. Gigante
        is_sa | (capital > 5_000_000) | (porte == 5),  # 3. Grande Empresa
        (capital > 1_000_000),  # 4. Média Empresa
        (porte == 1) | (porte == 3) | (capital <= 1_000_000),  # 5. PME
    ]

    resultados = [
        "SETOR PUBLICO",
        "GIGANTE / MULTINACIONAL",
        "GRANDE EMPRESA",
        "MÉDIA EMPRESA",
        "PME / PEQUENO NEGÓCIO",
    ]

    return np.select(condicoes, resultados, default="OUTROS")


def _buscar_dados_receita(con, cnpjs_unicos: pd.DataFrame, path_rf_empresa: str, path_rf_estab: str) -> pd.DataFrame:
    query = """
        SELECT
            emp.cnpj_base,
            emp.natureza_juridica,
            emp.capital_social,
            emp.porte,
            estab.cnae_fiscal_principal,
        FROM cnpjs_unicos c
        JOIN read_parquet(?) emp
            ON c.cnpj_base = emp.cnpj_base
        LEFT JOIN read_parquet(?) estab
            ON emp.cnpj_base = estab.cnpj_basico
        QUALIFY ROW_NUMBER() OVER (PARTITION BY emp.cnpj_base ORDER BY emp.cnpj_base) = 1
    """
    df_rf = con.execute(query, [path_rf_empresa, path_rf_estab]).df()
    df_rf["cnpj_base"] = df_rf["cnpj_base"].astype(str).str.zfill(8)
    return df_rf


def _aplicar_receita_e_cnae(
    df_origem: pd.DataFrame,
    df_rf: pd.DataFrame,
    cnpj_base_col: str,
    empresa_polo_cnpj: str,
    categoria: str,
    setor_atuacao: str,
    cnae_fiscal_principal: str,
    manter_detalhes: bool = True,
) -> pd.DataFrame:
    df_origem = df_origem.copy()
    df_origem[cnpj_base_col] = (
        df_origem[empresa_polo_cnpj]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .str[:8]
        .str.zfill(8)
    )

    df_merge = df_origem.merge(
        df_rf.rename(
            columns={
                "cnpj_base": cnpj_base_col,
                "cnae_fiscal_principal": cnae_fiscal_principal,
            }
        ),
        on=cnpj_base_col,
        how="left",
    )

    df_merge[categoria] = _classificar_porte_vetorizado(df_merge)
    df_merge[setor_atuacao] = _traduzir_setor_cnae(df_merge[cnae_fiscal_principal])

    if not manter_detalhes:
        df_merge = df_merge.drop(columns=["natureza_juridica", "capital_social", "porte"], errors="ignore")

    return df_merge


def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    base_path_processos = BASE_DIR / "data" / "silver" / "processos.parquet"
    base_path_rf_empresa = BASE_DIR / "data" / "bronze" / "base_receita_consolidada.parquet"
    base_path_rf_estab = BASE_DIR / "data" / "bronze" / "estabelecimentos_consolidado.parquet"
    processed_path_processos = BASE_DIR / "data" / "gold" / "detalhe_processos.parquet"

    df_proc = pd.read_parquet(str(base_path_processos))

    cnpj_ativo = (
        df_proc["empresa_polo_ativo_cnpj"].astype(str).str.replace(r"\D", "", regex=True).str[:8].str.zfill(8)
    )
    cnpj_passivo = (
        df_proc["empresa_polo_passivo_cnpj"].astype(str).str.replace(r"\D", "", regex=True).str[:8].str.zfill(8)
    )

    cnpjs_unicos = pd.DataFrame({"cnpj_base": pd.concat([cnpj_ativo, cnpj_passivo]).dropna().unique()})

    con = duckdb.connect()
    df_rf = _buscar_dados_receita(con, cnpjs_unicos, str(base_path_rf_empresa), str(base_path_rf_estab))
    con.close()

    df_proc = _aplicar_receita_e_cnae(
        df_proc,
        df_rf,
        cnpj_base_col="cnpj_base_ativo",
        empresa_polo_cnpj="empresa_polo_ativo_cnpj",
        manter_detalhes=False,
        categoria="categoria_ativo",
        setor_atuacao="setor_atuacao_ativo",
        cnae_fiscal_principal="cnae_fiscal_principal_ativo",
    )

    df_proc = _aplicar_receita_e_cnae(
        df_proc,
        df_rf,
        cnpj_base_col="cnpj_base_passivo",
        empresa_polo_cnpj="empresa_polo_passivo_cnpj",
        manter_detalhes=False,
        categoria="categoria_passivo",
        setor_atuacao="setor_atuacao_passivo",
        cnae_fiscal_principal="cnae_fiscal_principal_passivo",
    )

    df_proc.to_parquet(str(processed_path_processos))

    return df_proc