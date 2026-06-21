import re
import pandas as pd
from pathlib import Path

REGEX_UF = re.compile(r'-([A-Z]{2})\b')

MAPEAMENTO_ESTADOS = {
    'acre': 'AC',
    'alagoas': 'AL',
    'amapá': 'AP',
    'amapa': 'AP',
    'amazonas': 'AM',
    'bahia': 'BA',
    'ceará': 'CE',
    'ceara': 'CE',
    'distrito federal': 'DF',
    'espírito santo': 'ES',
    'espirito santo': 'ES',
    'goiás': 'GO',
    'goias': 'GO',
    'maranhão': 'MA',
    'maranhao': 'MA',
    'mato grosso': 'MT',
    'mato grosso do sul': 'MS',
    'minas gerais': 'MG',
    'pará': 'PA',
    'para': 'PA',
    'paraíba': 'PB',
    'paraiba': 'PB',
    'paraná': 'PR',
    'parana': 'PR',
    'pernambuco': 'PE',
    'piauí': 'PI',
    'piaui': 'PI',
    'rio de janeiro': 'RJ',
    'rio grande do norte': 'RN',
    'rio grande do sul': 'RS',
    'rondônia': 'RO',
    'rondonia': 'RO',
    'roraima': 'RR',
    'santa catarina': 'SC',
    'são paulo': 'SP',
    'sao paulo': 'SP',
    'sergipe': 'SE',
    'tocantins': 'TO',
}

def _load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype={'Número do Processo': str})
    df = df[df['Data de Distribuição'].notna()]

    df['Número do Processo'] = (
        df['Número do Processo']
        .astype(str)
        .str.replace(r'\D', '', regex=True)
        .str.zfill(20)
    )

    return df

def _extrair_estado(jurisdicao):
    if pd.isna(jurisdicao):
        return None
    texto = str(jurisdicao).strip()
    match = REGEX_UF.search(texto)
    if match:
        return match.group(1)
    texto_lower = texto.lower()
    for estado, uf in MAPEAMENTO_ESTADOS.items():
        if re.search(rf'\b{re.escape(estado)}\b', texto_lower):
            return uf
    return None

def _filtrar_estados(df: pd.DataFrame) -> pd.DataFrame:
    ESTADOS_AMAZONIA_LEGAL = {
        'AC', 'AM', 'AP', 'MA', 'MT', 'PA', 'RO', 'RR', 'TO'
    }
    df = df.copy()
    df['estado'] = df['Jurisdição'].apply(_extrair_estado)
    return df[df['estado'].isin(ESTADOS_AMAZONIA_LEGAL)]

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    base_path_processos = BASE_DIR / "data" / "bronze" / "trf1_completos.xlsx"
    processed_path_processos = BASE_DIR / "data" / "bronze" / "trf1_filtrados.xlsx"

    df_processos = _load_data(str(base_path_processos))
    df_processos = _filtrar_estados(df_processos)

    df_processos.to_excel(str(processed_path_processos), index=False)

    return df_processos