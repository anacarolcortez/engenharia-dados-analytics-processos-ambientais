import sys
from pathlib import Path

file = Path(__file__).resolve()
parent = file.parent.parent
sys.path.append(str(parent))

from pipeline.gold import detalhamento
import pipeline.silver.processos as processos
import pipeline.bronze.filtragem_estados as filtragem_estados


if __name__ == "__main__":

    print("Iniciando pipeline...")
    df_filtro_estados = filtragem_estados.run_pipeline()
    print(f"Total de processos após filtragem: {len(df_filtro_estados)}")

    df_processos = processos.run_pipeline()
    print(f"Total de processos com empresas processadas: {len(df_processos)}")
    print(f"Período: {df_processos['ano_distribuicao'].min()} - {df_processos['ano_distribuicao'].max()}")

    print("Enriquecendo base de processos...")
    df_processos_classificados = detalhamento.run_pipeline()
    print(f"Total de processos enriquecidos: {len(df_processos_classificados)}")