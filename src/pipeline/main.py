import sys
from pathlib import Path

file = Path(__file__).resolve()
parent = file.parent.parent
sys.path.append(str(parent))

from pipeline.gold import detalhamento
import pipeline.silver.processos as processos
import pipeline.silver.empresas as empresas


if __name__ == "__main__":

    print("Iniciando pipeline...")
    df_processos = processos.run_pipeline()
    print(f"Total de processos: {len(df_processos)}")
    print(f"Período: {df_processos['ano_distribuicao'].min()} - {df_processos['ano_distribuicao'].max()}")

    print("Gerando base de empresas...")
    df_empresas = empresas.run_pipeline()
    print(f"Total de empresas: {len(df_empresas)}")

    print("Enriquecendo base de empresas e processos...")
    df_empresas_classificadas, df_processos_classificados = detalhamento.run_pipeline()
    print(f"Total de empresas classificadas: {len(df_empresas_classificadas)}")
    print(f"Total de processos enriquecidos: {len(df_processos_classificados)}")