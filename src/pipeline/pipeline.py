import re
from duckdb import df
import pandas as pd
from pathlib import Path

MAPA_EMPRESAS = {
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVAVEIS - IBAMA': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVÁVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DOS RECURSOS NATURAIS RENOVÁVEIS - IBAMA': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DE RECURSOS NATURAIS RENOVÁVEIS': 'IBAMA',
    'INSTITUTO BRASILEIRO DO MEIO AMBIENTE E DE RECURSOS NATURAIS RENOVÁVEIS - IBAMA': 'IBAMA',
    'IBAMA': 'IBAMA',
    'INSTITUTO NACIONAL DE COLONIZAÇÃO E REFORMA AGRÁRIA': 'INCRA',
    'INSTITUTO NACIONAL DE COLONIZACAO E REFORMA AGRARIA': 'INCRA',
    'INCRA': 'INCRA',
    'MINISTÉRIO PÚBLICO FEDERAL': 'MPF',
    'MINISTERIO PUBLICO FEDERAL': 'MPF',
    'MPF': 'MPF',
}

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype={'Número do Processo': str})
    df = df[df['Data de Distribuição'].notna()]
    return df

def tipo_parte(texto):  
    if pd.isna(texto):
        return None

    texto = texto.upper()

    if 'CNPJ' in texto:
        return 'empresa'
    if 'CPF' in texto:
        return 'pessoa_fisica'
    return 'outro'

def extrair_estado(jurisdicao):
    if pd.isna(jurisdicao):
        return None
    
    match = re.search(r'-([A-Z]{2})', jurisdicao)
    if match:
        return match.group(1)
    
    mapeamento = {
        'Acre': 'AC',
        'Alagoas': 'AL',
        'Amapá': 'AP',
        'Amapa': 'AP',
        'Amazonas': 'AM',
        'Bahia': 'BA',
        'Ceará': 'CE',
        'Ceara': 'CE',
        'Distrito Federal': 'DF',
        'Espírito Santo': 'ES',
        'Espirito Santo': 'ES',
        'Goiás': 'GO',
        'Goias': 'GO',
        'Maranhão': 'MA',
        'Maranhao': 'MA',
        'Mato Grosso': 'MT',
        'Mato Grosso do Sul': 'MS',
        'Minas Gerais': 'MG',
        'Pará': 'PA',
        'Para': 'PA',
        'Paraíba': 'PB',
        'Paraiba': 'PB',
        'Paraná': 'PR',
        'Parana': 'PR',
        'Pernambuco': 'PE',
        'Piauí': 'PI',
        'Piaui': 'PI',
        'Rio de Janeiro': 'RJ',
        'Rio Grande do Norte': 'RN',
        'Rio Grande do Sul': 'RS',
        'Rondônia': 'RO',
        'Rondonia': 'RO',
        'Roraima': 'RR',
        'Santa Catarina': 'SC',
        'São Paulo': 'SP',
        'Sao Paulo': 'SP',
        'Sergipe': 'SE',
        'Tocantins': 'TO'
    }
    
    for nome, uf in mapeamento.items():
        if nome in jurisdicao:
            return uf
            
    return None

def normalizar_empresa(nome):
    if pd.isna(nome):
        return None

    nome = nome.upper().strip()

    for k, v in MAPA_EMPRESAS.items():
        if k in nome:
            return v

    return nome

def extrair_empresa(texto):
    if pd.isna(texto):
        return pd.Series([None, None])

    texto = texto.replace('\n', ' ')

    partes = [p.strip() for p in texto.split(',')]

    for parte in partes:
        if 'CNPJ' in parte:
            match = re.search(r'(.*?)\s*-\s*CNPJ:\s*([\d./-]+)', parte)

            if match:
                nome = match.group(1).strip()
                cnpj = match.group(2).strip()

                termos_ruido = [
                    r'\(IMPETRADO\)', r'\[ATIVO\]', r'\[PASSIVO\]', r'\(REU\)',
                    r'CHEFE\s*-\s*', r'SUPERINTENDENTE\s*.*?\s*-\s*',
                    r'DIRETOR\s*.*?\s*-\s*', r'COORDENADOR\s*.*?\s*-\s*'
                ]

                for ruido in termos_ruido:
                    nome = re.sub(ruido, '', nome, flags=re.IGNORECASE).strip()

                nome = re.sub(r'^[,\-\s]+', '', nome).upper()

                return pd.Series([nome, cnpj])

    return pd.Series([None, None])

def anonimizar_status(status):
    if pd.isna(status):
        return status

    return re.sub(r'(?<=prazo de\s)[A-ZÀ-Úa-zà-ÿ\s]+(?=\sem)', ' PESSOA ', status, flags=re.IGNORECASE)

def transform_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df['assunto_codigo'] = (
        df['Assunto']
        .str.extract(r'\((\d+)\)')
        .astype('Int64')
    )

    df['assunto'] = (
        df['Assunto']
        .str.split(' - ').str[0]
        .str.split('(').str[0]
        .str.strip()
        .str.upper()
    )

    df['orgao_nome'] = df['Órgão Julgador'].str.split('Endereço').str[0].str.strip()
    df['data_distribuicao'] = pd.to_datetime(
        df['Data de Distribuição'],
        format='%d/%m/%Y',
        errors='coerce'
    )
    df['ano_distribuicao'] = df['data_distribuicao'].dt.year.astype('Int64')
    df['classe_judicial'] = df['Classe Judicial'].str.split('(').str[0].str.strip()
    df['estado'] = df['Jurisdição'].apply(extrair_estado)
    df['ultima_movimentacao'] = pd.to_datetime(
        df['Status'].str.extract(r'(\d{2}/\d{2}/\d{4})')[0],
        format='%d/%m/%Y',
        errors='coerce'
    )
    df['ano_ultima_movimentacao'] = df['ultima_movimentacao'].dt.year.astype('Int64')
    df['tem_movimentacao'] = df['ultima_movimentacao'].notna()
    df['qtd_partes_ativas'] = df['Polo Ativo'].str.count(',') + 1
    df['tipo_parte_passiva'] = df['Polo Passivo'].apply(tipo_parte)
    df[['empresa_nome', 'empresa_cnpj']] = df['Polo Passivo'].apply(extrair_empresa)
    df['empresa_nome'] = df['empresa_nome'].apply(normalizar_empresa)    
    df['tem_advogado'] = df['Polo Ativo'].str.contains('ADVOGADO', na=False)
    df['tempo_processo_dias'] = (
        df['ultima_movimentacao'] - df['data_distribuicao']
    ).dt.days

    df = df[df['empresa_cnpj'].notna()]

    mask = df['tipo_parte_passiva'] == 'empresa'
    df.loc[mask, 'Status'] = df.loc[mask, 'Status'].apply(anonimizar_status)
    
    df['status_clean'] = df['Status'].str.upper()
    df['finalizado'] = df['status_clean'].str.contains('BAIXADO|ARQUIVADO', na=False)

    return df


def build_analytical_dataset(df: pd.DataFrame) -> pd.DataFrame:

    colunas = [
        'Número do Processo',
        'assunto_codigo',
        'assunto',
        'Jurisdição',
        'orgao_nome',
        'classe_judicial',
        'estado',
        'status_clean',
        'qtd_partes_ativas',
        'tipo_parte_passiva',
        'empresa_nome',
        'empresa_cnpj',
        'tem_advogado',
        'ano_distribuicao',
        'ano_ultima_movimentacao',
        'tempo_processo_dias',
        'finalizado'
    ]

    df_final = df[colunas].copy()

    df_final = df_final.rename(columns={
        'Número do Processo': 'numero_processo',
        'Jurisdição': 'jurisdicao',
        'status_clean': 'status',
    })

    return df_final

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    raw_path = BASE_DIR / "data" / "raw" / "processos_teste.xlsx"
    processed_path = BASE_DIR / "data" / "processed" / "processos.parquet"
    
    df = load_data(str(raw_path))
    df = transform_data(df)
    df_final = build_analytical_dataset(df)

    df_final.to_parquet(str(processed_path), index=False)

    return df_final


if __name__ == "__main__":
    df_final = run_pipeline()
    print(f"Total de registros: {len(df_final)}")
    print(f"Período: {df_final['ano_distribuicao'].min()} - {df_final['ano_distribuicao'].max()}")