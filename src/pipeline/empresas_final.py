import pandas as pd
from pathlib import Path

def _load_data(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)

def _limpar_e_converter(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        valor_limpo = str(valor).replace('.', '').replace(',', '.')
        return float(valor_limpo)
    except:
        return 0.0
    
def _classificar_porte_real(row):
    nj = str(row['natureza_juridica']).replace('-', '').replace('.', '')
    nome = str(row['empresa_nome']).upper()

    try:
        porte = int(float(row['porte']))
    except:
        porte = -1

    capital = _limpar_e_converter(row['capital_social'])

    # HIERARQUIA DE CLASSIFICAÇÃO

    # Setor Público: Série 100
    if nj.startswith('1'):
        return 'SETOR PUBLICO'

    # S.A. nunca é PME por lei
    # Códigos que começam com 205 ou 204
    if nj.startswith('204') or nj.startswith('205') or 'S.A.' in nome or 'S/A' in nome:
        return 'GRANDE EMPRESA'

    # Capital inicial acima de 1 milhão
    if capital > 1000000:
        return 'GRANDE EMPRESA'

    # Porte informado na RF é 1 ou 0 (grandes/médias)
    if porte == 0 or porte == 1:
        return 'GRANDE EMPRESA'

    # PME (Se o porte for 3 ou 5 E não passou nas regras de S.A.)
    if porte == 3 or porte == 5:
        return 'PME'

    return 'OUTROS'

def _transformar_com_receita(df_processos, path: str) -> pd.DataFrame:
    colunas_interesse = ['cnpj_base', 'natureza_juridica', 'capital_social', 'porte']
    df_rf = pd.read_parquet(str(path), columns=colunas_interesse)

    df_processos['cnpj_base'] = df_processos['empresa_cnpj'].str.replace(r'\D', '', regex=True).str[:8]

    df_merge = pd.merge(df_processos, df_rf, on='cnpj_base', how='left')
    df_merge['categoria'] = df_merge.apply(_classificar_porte_real, axis=1)

    return df_merge

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    original_path = BASE_DIR / "data" / "processed" / "empresas.parquet"
    original_path_rf = BASE_DIR / "data" / "raw" / "receita_federal_sample.parquet"
    processed_path = BASE_DIR / "data" / "processed" / "insustentaveis.parquet"

    df = _load_data(str(original_path))
    df_final = _transformar_com_receita(df, original_path_rf)
    df_final.to_parquet(str(processed_path))
    return df_final
