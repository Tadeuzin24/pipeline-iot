# Pipeline de Dados IoT com Docker

## 1. Objetivo

Este projeto implementa um pipeline de dados para processar leituras históricas de temperatura de dispositivos IoT, armazená-las em um banco PostgreSQL e apresentar os resultados em um dashboard interativo.

O projeto utiliza dados do conjunto Temperature Readings: IoT Devices, disponibilizado no Kaggle.

## 2. Tecnologias utilizadas

- Python: processamento dos dados.
- Pandas: leitura, limpeza e transformação do CSV.
- Docker: execução do PostgreSQL em um contêiner.
- PostgreSQL: armazenamento e consulta dos dados.
- SQLAlchemy: conexão entre Python e PostgreSQL.
- Streamlit: interface do dashboard.
- Plotly: criação dos gráficos interativos.
- Git e GitHub: versionamento e publicação do código.

## 3. Fonte dos dados

Conjunto de dados: Temperature Readings: IoT Devices.

Link: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

O arquivo CSV utilizado é `IOT-temp.csv` e deve ser colocado na pasta `data/`.

## 4. Estrutura do projeto

```text
pipeline-iot/
├── data/
│   └── .gitkeep
├── docs/
├── screenshots/
│   ├── dashboard-graficos.png
│   └── dashboard-indicadores.png
├── sql/
│   └── views.sql
├── src/
│   ├── ingest.py
│   └── dashboard.py
├── .gitignore
├── README.md
└── requirements.txt
```

**Observação:** o arquivo `IOT-temp.csv` não é versionado no GitHub. Para executar o projeto, baixe o conjunto de dados indicado na seção 3 e coloque o arquivo na pasta `data/` com esse nome.
```

## 5. Configuração do ambiente

Requisitos:
- Python 3.11 ou compatível.
- Docker Desktop.
- Git.

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

## 6. Banco de dados PostgreSQL com Docker

Na primeira execução, crie o contêiner:

```powershell
docker run --name postgres-iot `
  -e POSTGRES_USER=iot_user `
  -e POSTGRES_PASSWORD=iot_dev_2026 `
  -e POSTGRES_DB=iot_data `
  -p 5433:5432 `
  -v postgres_iot_data:/var/lib/postgresql/data `
  -d postgres:16
```

Se o contêiner já existir, mas estiver parado, inicie-o:

```powershell
docker start postgres-iot
```

Verifique se o banco está pronto:

```powershell
docker exec postgres-iot pg_isready -U iot_user -d iot_data
```

A senha acima é destinada ao ambiente local de demonstração. Em outras instalações, utilize uma senha própria e configure a variável de ambiente `DB_PASSWORD` com o mesmo valor.

## 7. Importação dos dados

Baixe o arquivo CSV do Kaggle e coloque-o em `data/IOT-temp.csv`.

Defina a senha no PowerShell:

```powershell
$env:DB_PASSWORD = "iot_dev_2026"
```

Execute o script de ingestão:

```powershell
python .\src\ingest.py
```

O script:
- Lê o arquivo CSV.
- Ajusta os nomes das colunas.
- Converte datas e temperaturas.
- Remove registros com campos essenciais inválidos.
- Insere os dados no PostgreSQL.

Na execução realizada durante o desenvolvimento, foram importados 97.606 registros, sem registros descartados.

## 8. Views SQL

O arquivo `sql/views.sql` contém quatro views:

### avg_temp_por_sala

Calcula a temperatura média e a quantidade de leituras por sala.

### leituras_por_hora

Apresenta a quantidade de leituras agrupadas por hora do dia.

### temp_max_min_por_dia

Calcula as temperaturas máxima, mínima e média para cada dia.

### avg_temp_por_origem

Compara as temperaturas médias e a quantidade de leituras por origem, diferenciando as categorias internas e externas.

Para aplicar as views, execute:

```powershell
docker cp .\sql\views.sql postgres-iot:/tmp/views.sql
docker exec postgres-iot psql -U iot_user -d iot_data -f /tmp/views.sql
```

A importação dos dados deve ser realizada antes da criação das views em uma instalação nova.

## 9. Execução do dashboard

Defina a variável de ambiente no PowerShell:

```powershell
$env:DB_PASSWORD = "iot_dev_2026"
```

Execute o dashboard:

```powershell
streamlit run .\src\dashboard.py
```

Abra o endereço local informado pelo Streamlit, normalmente:

http://localhost:8501

O dashboard apresenta indicadores gerais e três visualizações interativas:

1. Temperatura média por origem.
2. Quantidade de leituras por hora.
3. Temperaturas máxima e mínima por dia.

## 10. Capturas de tela

As capturas de tela do dashboard devem ser armazenadas na pasta `screenshots/`.

Arquivos previstos:

- `dashboard-indicadores.png`
- `dashboard-graficos.png`

As imagens devem mostrar o dashboard em funcionamento e seus principais gráficos.

## 11. Resultados obtidos

A importação inicial carregou 97.606 registros no PostgreSQL, sem descartar dados durante a validação realizada.

As consultas permitiram analisar a distribuição das leituras ao longo do dia e as variações de temperatura entre datas e categorias de origem.

A partir dessas informações, é possível identificar horários com maior volume de leituras e observar variações nas temperaturas registradas.

Os dados empregados são históricos. Portanto, o projeto demonstra processamento e análise de dados de sensores, mas não representa uma transmissão de dados IoT ao vivo.

## 12. Versionamento com Git

Os comandos utilizados para versionar e publicar o projeto são:

```powershell
git init
git add .
git commit -m "Projeto inicial: Pipeline de Dados IoT"
git branch -M main
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

Substitua `URL_DO_REPOSITORIO` pelo endereço do repositório criado no GitHub.

O arquivo `.gitignore` evita publicar o ambiente virtual, arquivos temporários, credenciais em arquivo `.env` e o CSV que pode ser baixado diretamente do Kaggle.

## 13. Possíveis aplicações práticas

Uma solução semelhante pode apoiar o monitoramento de temperatura em ambientes industriais, instalações comerciais e sistemas de monitoramento ambiental.

Com sensores adequados e uma infraestrutura de coleta contínua, uma arquitetura desse tipo pode auxiliar na identificação de variações relevantes, na análise de condições ambientais e na tomada de decisões operacionais.
