# 📚 Data Analytics com ETL

Projeto para exemplificar o trabalho de engenharia e análise de dados, utilizando extração de indicadores de processos ambientais em trâmite no TRF-1 (Amazônia Legal). Este repositório possui apenas fins didáticos, para demonstrar como trabalhar com os dados extraídos da API DataJud e minerados em mais detalhes pelo número do processo, por meio de webscraping no portal PJe. 

Neste projeto, transforma-se dados brutos em uma camada analítica performática utilizando DuckDB e Parquet. A pipeline simulou uma arquitetura medallion (camada bronze, silver e gold). 

    DataJud + PJe (excel) & Base CNPJ Receita Federal -> Bronze (Parquet) -> Silver (Cleaned) -> Gold (Analytics)

🏢 Arquitetura

    Engine: DuckDB (Processamento OLAP em memória)

    Armazenamento: Arquivos colunares Parquet (otimização de I/O)

    Backend: FastAPI

    Data Wrangling: Pandas e Regex (normalização e anonimização de dados semi-estruturados)

📈 Insights Analíticos e Recortes Jurídicos

O projeto aplica uma camada de inteligência jurídica para categorizar processos além das etiquetas básicas do tribunal, permitindo recortes por:

    Severidade de Risco: Classificação entre risco Alto (ex: Danos Ambientais), Médio (ex: Multas) e Baixo (ex: Taxas Administrativas).

    Temas Especializados: Identificação de pautas críticas como Mineração, Proteção de Flora/APP, Unidades de Conservação e Licenciamento.

    Visão Financeira vs. Operacional: Separação entre processos de arrecadação (Tributário/TCFA) e processos de execução patrimonial (Dívida Ativa).

    Eficiência Processual: Monitoramento da taxa de encerramento de processos e tempo médio de tramitação por categoria específica

    Classificação Econômica: Porte baseado no poder econômico real, cruzando CNPJs litigates com dados da Receita Federal. 

🛠 Como executar

    Instale as dependências: pip install -r requirements.txt

    Processe os dados: python src/pipeline/main.py

    Suba a API: uvicorn src.app.api:app --reload

    Acessar os endpoints: http://127.0.0.1:8000/docs

    Visualizar gráficos: streamlit run src/dashboard/dashboard.py 

🧪 Por que DuckDB?

Escolhi o DuckDB por sua capacidade de executar consultas SQL complexas diretamente em arquivos Parquet, sendo ideal para cenários de Data Analytics onde a performance de leitura e agregação é prioridade, sem a necessidade de um servidor de banco de dados tradicional. Alternativa open source e gratuita.

📊 Visualização dos Dados (Dashboard)

Uma demonstração do dashboard interativo desenvolvido com Streamlit:

![Dashboard Analytics TRF1](graficos.png)

Também é possível visualizar em PDF (gerado do deploy do Streamlit)

------------------------------------------
OBS: Como a base original possui mais de 80 mil processos, expus apenas uma simulação com uma amostra bem pequena (menos de 1%) e não-representativa do todo, que inseri para testes.