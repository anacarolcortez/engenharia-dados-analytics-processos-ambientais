import re
import pandas as pd
from pathlib import Path

MAPA_EMPRESAS = {
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS - IBAMA': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVÁVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVÁVEIS - IBAMA': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DE RECURSOS NATURAIS RENOVÁVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DE RECURSOS NATURAIS RENOVÁVEIS - IBAMA': 'IBAMA',
    'INSTITUTO BRASILEIRO DE MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DE MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS - IBAMA': 'IBAMA',
    'IBAMA': 'IBAMA',
    'INSTITUTO NACIONAL DE COLONIZAÇÃO E REFORMA AGRÁRIA': 'INCRA',
    'INSTITUTO NACIONAL DE COLONIZACAO E REFORMA AGRARIA': 'INCRA',
    'INCRA': 'INCRA',
    'MINISTÉRIO PÚBLICO FEDERAL': 'MPF',
    'MINISTERIO PUBLICO FEDERAL': 'MPF',
    'MPF': 'MPF',
}

TERMOS_RUIDO = [
    re.compile(r'\(IMPETRADO\)', re.IGNORECASE),
    re.compile(r'\[ATIVO\]', re.IGNORECASE),
    re.compile(r'\[PASSIVO\]', re.IGNORECASE),
    re.compile(r'\(REU\)', re.IGNORECASE),
    re.compile(r'CHEFE\s*-\s*', re.IGNORECASE),
    re.compile(r'SUPERINTENDENTE\s*.*?\s*-\s*', re.IGNORECASE),
    re.compile(r'DIRETOR\s*.*?\s*-\s*', re.IGNORECASE),
    re.compile(r'COORDENADOR\s*.*?\s*-\s*', re.IGNORECASE)
]

REGEX_CNPJ = re.compile(r'(.*?)\s*-\s*CNPJ:\s*([\d./-]+)')
REGEX_ADVOGADO = re.compile(r'(.*?)\s*-\s*(OAB\s+\w+)', re.IGNORECASE)

def _load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype={'Número do Processo': str})
    df = df[df['Data de Distribuição'].notna()]
    return df

def _tipo_parte(texto):
    if pd.isna(texto):
        return None
    texto = str(texto).upper()
    if 'CNPJ' in texto:
        return 'empresa'
    if 'CPF' in texto:
        return 'pessoa_fisica'
    return 'outro'

def _normalizar_empresa(nome):
    if pd.isna(nome):
        return None
    nome_clean = str(nome).upper().strip()
    for k, v in MAPA_EMPRESAS.items():
        if k in nome_clean:
            return v
    return nome_clean

def _extrair_empresa(texto):
    if pd.isna(texto):
        return pd.Series([None, None], index=['empresa_nome', 'empresa_cnpj'])

    texto = str(texto).replace('\n', ' ')
    partes = [p.strip() for p in texto.split(',')]

    for parte in partes:
        if 'CNPJ' in parte:
            match = REGEX_CNPJ.search(parte)
            if match:
                nome = match.group(1).strip()
                cnpj = match.group(2).strip()

                for ruido in TERMOS_RUIDO:
                    nome = ruido.sub('', nome).strip()

                nome = re.sub(r'^[,\-\s]+', '', nome).upper()
                return pd.Series([nome, cnpj], index=['empresa_nome', 'empresa_cnpj'])

    primeiro_nome = partes[0].split('-')[0].strip().upper() if partes else None
    return pd.Series([primeiro_nome, None], index=['empresa_nome', 'empresa_cnpj'])

def _categorizar_juridico(texto):
    if pd.isna(texto):
        return "NÃO INFORMADO"

    t = str(texto).upper()

    if any(kw in t for kw in ['AUXÍLIO EMERGENCIAL', 'ASSISTENCIAL', 'SEGURO-DEFESO', 'PREVIDENCIÁRIO', 'SINDICAL']):
        return "OUTROS (NÃO AMBIENTAL)"

    if any(kw in t for kw in ['RESERVA LEGAL', 'ÁREA DE PRESERVAÇÃO PERMANENTE', 'APP', 'FLORA', 'FLORESTAS', 'MATA ATLÂNTICA']):
        return "PROTEÇÃO DE VEGETAÇÃO (FLORA/APP)"

    if 'MINERAÇÃO' in t or 'RECURSOS MINERAIS' in t or 'MINERACAO' in t:
        return "MINERAÇÃO"

    if 'TAXA DE FISCALIZAÇÃO AMBIENTAL' in t or 'TCFA' in t:
        return "TRIBUTÁRIO (TCFA)"

    if any(kw in t for kw in ['MULTA', 'SANÇÃO', 'SANCOES', 'INFRAÇÃO', 'APREENSÃO', 'INTERDIÇÃO', 'EMBARGO']):
        return "MULTA / INFRAÇÃO AMBIENTAL"

    if 'UNIDADE DE CONSERVAÇÃO' in t:
        return "UNIDADE DE CONSERVAÇÃO"

    if 'FAUNA' in t or 'PESCA' in t:
        return "FAUNA / PESCA"

    if 'PATRIMÔNIO CULTURAL' in t or 'HISTÓRICO' in t:
        return "PATRIMÔNIO CULTURAL / HISTÓRICO"

    if 'DESAPROPRIAÇÃO' in t or 'DESAPROPRIACAO' in t:
        return "DESAPROPRIAÇÃO"

    if any(kw in t for kw in ['POSSE', 'ESBULHO', 'TURBAÇÃO', 'PROPRIEDADE', 'REINTEGRAÇÃO']):
        return "DISPUTA POSSESSÓRIA"

    if 'LICENÇA' in t or 'LICENCIMENTO' in t:
        return "LICENCIAMENTO AMBIENTAL"

    if any(kw in t for kw in ['DANO AMBIENTAL', 'POLUIÇÃO', 'DEGRADAÇÃO', 'HÍDRICOS', 'AGROTÓXICOS']):
        return "DANO / REPARAÇÃO AMBIENTAL"

    if 'DÍVIDA ATIVA' in t:
        return "EXECUÇÃO DE DÍVIDA ATIVA"

    if 'NULIDADE DE ATO' in t or 'PROCESSO ADMINISTRATIVO' in t:
        return "ADMINISTRATIVO (NULIDADE/RITO)"

    return "OUTROS TEMAS AMBIENTAIS"

def _extrair_advogados(texto):
    if pd.isna(texto):
        return None

    texto = str(texto).replace('\n', ' ')
    partes = [p.strip() for p in texto.split(',')]
    advogados_encontrados = []

    for parte in partes:
        if 'ADVOGADO' in parte.upper():
            match = REGEX_ADVOGADO.search(parte)
            if match:
                nome = match.group(1).strip().upper()
                oab = match.group(2).strip().upper()
                advogados_encontrados.append(f"{nome} - {oab}")

    return ", ".join(advogados_encontrados) if advogados_encontrados else None

def _transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Mapeamento do Assunto
    df['assunto_especifico'] = df['Assunto'].apply(_categorizar_juridico)
    df['assunto_codigo'] = df['Assunto'].str.extract(r'\((\d+)\)').astype('Int64')
    df['assunto_raiz'] = (
        df['Assunto']
        .str.split(' - ').str[0]
        .str.split('(').str[0]
        .str.strip()
        .str.upper()
    )

    # Dados do Processo
    df['orgao_nome'] = df['Órgão Julgador'].str.split('Endereço').str[0].str.strip()
    df['data_distribuicao'] = pd.to_datetime(df['Data de Distribuição'], format='%d/%m/%Y', errors='coerce')
    df['ano_distribuicao'] = df['data_distribuicao'].dt.year.astype('Int64')
    df['classe_judicial'] = df['Classe Judicial'].str.split('(').str[0].str.strip()
    df['estado'] = df['estado'].str.upper()
    df['ultima_movimentacao'] = pd.to_datetime(df['Status'].str.extract(r'(\d{2}/\d{2}/\d{4})')[0], format='%d/%m/%Y', errors='coerce')
    df['ano_ultima_movimentacao'] = df['ultima_movimentacao'].dt.year.astype('Int64')
    df['tempo_processo_dias'] = (df['ultima_movimentacao'] - df['data_distribuicao']).dt.days

    # ENRIQUECIMENTO: POLO ATIVO
    df[['empresa_polo_ativo_nome', 'empresa_polo_ativo_cnpj']] = df['Polo Ativo'].apply(_extrair_empresa)
    df['empresa_polo_ativo_nome'] = df['empresa_polo_ativo_nome'].apply(_normalizar_empresa)
    df['adv_ativo'] = df['Polo Ativo'].apply(_extrair_advogados)

    # ENRIQUECIMENTO: POLO PASSIVO
    df[['empresa_polo_passivo_nome', 'empresa_polo_passivo_cnpj']] = df['Polo Passivo'].apply(_extrair_empresa)
    df['empresa_polo_passivo_nome'] = df['empresa_polo_passivo_nome'].apply(_normalizar_empresa)
    df['adv_passivo'] = df['Polo Passivo'].apply(_extrair_advogados)

    # Status final do processo
    df = df[df['empresa_polo_passivo_cnpj'].notna()]
    df['status'] = df['Status'].str.upper()
    df['finalizado'] = df['status'].str.contains('BAIXADO|ARQUIVADO', na=False)

    return df

def _build_analytical_dataset(df: pd.DataFrame) -> pd.DataFrame:
    colunas = [
        'Número do Processo', 'assunto_codigo', 'assunto_raiz', 'assunto_especifico',
        'Jurisdição', 'orgao_nome', 'classe_judicial', 'estado', 'orgao_processo', 'cidade_processo',
        'status', 'empresa_polo_ativo_nome', 'empresa_polo_ativo_cnpj', 'adv_ativo',
        'empresa_polo_passivo_nome', 'empresa_polo_passivo_cnpj', 'adv_passivo',
        'ano_distribuicao', 'ano_ultima_movimentacao', 'tempo_processo_dias', 'finalizado'
    ]

    df_final = df[colunas].copy()
    df_final = df_final.rename(columns={
        'Número do Processo': 'numero_processo',
        'Jurisdição': 'jurisdicao',
        'assunto_raiz': 'assunto'
    })

    return df_final

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    raw_path = BASE_DIR / "data" / "bronze" / "trf1_filtrados.xlsx"
    processed_path = BASE_DIR / "data" / "silver" / "processos.parquet"

    df = _load_data(str(raw_path))
    df = _transform_data(df)
    df_final = _build_analytical_dataset(df)

    df_final.to_parquet(str(processed_path), index=False)
    return df_final