📚 Data Analytics com ETL

Projeto para exemplificar o trabalho de engenharia e análise de dados, utilizando extração de indicadores de processos ambientais em trâmite no TRF-1.A base de dados foi reduzida da original (que inclui mais de 80 mil processos) para fins didáticos, pois o foco do repositório é demonstrar como trabalhar com os dados extraídos da API DataJud e coletados em detalhes, pelo número do processo, por meio de webscraping no portal PJe. 

Neste projeto, transforma-se dados brutos (Excel) em uma camada analítica performática utilizando DuckDB e Parquet.

🚀 Arquitetura

    Engine: DuckDB (Processamento OLAP em memória)

    Armazenamento: Arquivos colunares Parquet (otimização de I/O)

    Backend: FastAPI

    Data Wrangling: Pandas e Regex para limpeza

📊 Insights Analíticos Incluídos

    Ranking de Litigiosidade: Identificação das empresas com maior volume de processos.

    KPI de Performance: Tempo médio de tramitação por estado e órgão julgador.

    Detecção de Sazonalidade: Volume de novos processos ao longo do tempo.

🛠 Como executar

    Instale as dependências: pip install -r requirements.txt

    Processe os dados: python src/pipeline/pipeline.py

    Suba a API: uvicorn src.app.api:app --reload

    Acessar os endpoints: http://127.0.0.1:8000/docs

    Visualizar gráficos: streamlit run src/dashboard/dashboard.py 

🧪 Por que DuckDB?

Escolhi o DuckDB por sua capacidade de executar consultas SQL complexas diretamente em arquivos Parquet, sendo ideal para cenários de Data Analytics onde a performance de leitura e agregação é prioridade, sem a necessidade de um servidor de banco de dados tradicional.

## 📊 Visualização dos Dados (Dashboard)

Uma demonstração do dashboard interativo desenvolvido com Streamlit:

![Dashboard Analytics TRF1](graficos.png)

OBS: Os dados contidos no projeto não são representativos do todo, pois compreendem menos de 1% dos casos e não incluem grandes empresas, propositalmente. A amostra foi escolhida apenas para estudos de ETL