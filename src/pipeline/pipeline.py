import processos_final
import empresas_bruto
import empresas_final

if __name__ == "__main__":

    print("Iniciando pipeline...")
    df_processos = processos_final.run_pipeline()
    print(f"Total de processos: {len(df_processos)}")
    print(f"Período: {df_processos['ano_distribuicao'].min()} - {df_processos['ano_distribuicao'].max()}")

    print("Gerando base de empresas...")
    df_empresas = empresas_bruto.run_pipeline()
    print(f"Total de empresas: {len(df_empresas)}")

    print("Classificando empresas...")
    df_empresas_classificadas = empresas_final.run_pipeline()
    print(f"Total de empresas classificadas: {len(df_empresas_classificadas)}")
