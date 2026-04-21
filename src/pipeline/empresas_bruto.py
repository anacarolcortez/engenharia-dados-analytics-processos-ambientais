import pandas as pd
from pathlib import Path

def _load_data(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)

def _generate_empresas_parquet(df: pd.DataFrame, path: str) -> pd.DataFrame:
    resultado = df.groupby('empresa_cnpj').agg({
        'empresa_nome': 'first',
        'estado': 'first',
        'numero_processo': 'count'
    }).rename(columns={'numero_processo': 'quantidade'}).reset_index()

    resultado = resultado.sort_values(by='quantidade', ascending=False)
    resultado.to_parquet(str(path), index=False)
    return resultado

def run_pipeline():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    original_path = BASE_DIR / "data" / "processed" / "processos.parquet"
    processed_path = BASE_DIR / "data" / "processed" / "empresas.parquet"

    df = _load_data(str(original_path))
    df_final = _generate_empresas_parquet(df, processed_path)
    return df_final
