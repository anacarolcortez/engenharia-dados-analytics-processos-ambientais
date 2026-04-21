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

    # Análise por capital social
    if capital > 50000000 or nj.startswith('204') or nj.startswith('205'):
        return 'GIGANTE / MULTINACIONAL'

    # GRANDE EMPRESA
    if capital > 5000000 or 'S.A.' in nome or 'S/A' in nome:
        return 'GRANDE EMPRESA'

    # MÉDIA EMPRESA
    if capital > 1000000 or porte == 1:
        return 'MÉDIA EMPRESA'

    # PME (Pequenas e Micro)
    if porte == 3 or porte == 5 or capital <= 1000000:
        return 'PME / PEQUENO NEGÓCIO'

    # Porte informado na RF é 1 ou 0 (grandes/médias)
    if porte == 0 or porte == 1:
        return 'GRANDE EMPRESA'

    # PME (Se o porte for 3 ou 5 E não passou nas regras de S.A.)
    if porte == 3 or porte == 5:
        return 'PME'

    return 'OUTROS'

def _transformar_com_receita(df_empresas, path: str, manter_detalhes=True) -> pd.DataFrame:
    colunas_interesse = ['cnpj_base', 'natureza_juridica', 'capital_social', 'porte']
    df_rf = pd.read_parquet(str(path), columns=colunas_interesse)

    df_empresas['cnpj_base'] = df_empresas['empresa_cnpj'].str.replace(r'\D', '', regex=True).str[:8]

    df_merge = pd.merge(df_empresas, df_rf, on='cnpj_base', how='left')
    df_merge['categoria'] = df_merge.apply(_classificar_porte_real, axis=1)

    if not manter_detalhes:
        colunas_para_remover = ['natureza_juridica', 'capital_social', 'porte']
        df_merge = df_merge.drop(columns=colunas_para_remover)

    return df_merge

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    base_path_empresas = BASE_DIR / "data" / "silver" / "empresas.parquet"
    base_path_processos = BASE_DIR / "data" / "silver" / "processos.parquet"
    base_path_rf = BASE_DIR / "data" / "bronze" / "receita_federal_sample.parquet"
    processed_path_empresas = BASE_DIR / "data" / "gold" / "detalhe_empresas.parquet"
    processed_path_processos = BASE_DIR / "data" / "gold" / "detalhe_processos.parquet"

    # Tabela empresas enriquecida
    df = _load_data(str(base_path_empresas))
    df_empresas = _transformar_com_receita(df, base_path_rf)
    df_empresas.to_parquet(str(processed_path_empresas))

    # Tabela processos enriquecida
    df_processos = _load_data(str(base_path_processos))
    df_processos = _transformar_com_receita(df_processos, base_path_rf, manter_detalhes=False)
    df_processos.to_parquet(str(processed_path_processos))
    return df_empresas, df_processos
