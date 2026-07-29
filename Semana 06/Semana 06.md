# Semana 6 - Orquestração e Apache Airflow

## Orquestração

Nesta semana, o foco é entender como um pipeline de dados pode deixar de ser apenas um conjunto de scripts executados manualmente e passar a ser um fluxo controlado, monitorado e reexecutável.

Em um cenário ideal, um pipeline executa todas as etapas na ordem correta:

- extração dos dados;
- transformação e limpeza;
- validação;
- carga ou persistência do resultado.

Na prática, porém, pipelines podem apresentar atrasos, falhas, logs espalhados, duplicatas, execuções manuais fora de ordem e pouca rastreabilidade. A orquestração surge para controlar esse processo.

Orquestrar um pipeline significa definir:

- **quando** o fluxo deve executar;
- **quais tarefas** fazem parte do fluxo;
- **em qual ordem** as tarefas devem executar;
- **quais dependências** existem entre elas;
- **como observar** logs, estados e falhas;
- **como recuperar** a execução com retries, timeouts ou reprocessamento.

Também é importante diferenciar dois conceitos:

- **Fluxo de dados:** caminho percorrido pelos dados, por exemplo `API -> tratamento -> CSV`.
- **Fluxo de execução:** ordem em que as tarefas rodam, por exemplo `extrair -> transformar -> carregar`.

A orquestração coordena principalmente o fluxo de execução. Ela garante que uma etapa não comece apenas porque chegou o horário, mas sim porque suas dependências foram concluídas corretamente.

Um conceito central é a **DAG**, sigla para *Directed Acyclic Graph*, ou grafo direcionado acíclico.

Uma DAG é:

- **Direcionada:** as setas indicam dependência entre tarefas.
- **Acíclica:** não pode existir um ciclo, pois uma tarefa não deve depender dela mesma direta ou indiretamente.
- **Um grafo:** permite fluxos lineares, paralelos, ramificações e junções.

Exemplo de fluxo linear:

```text
extrair -> transformar -> carregar
```

Exemplo de paralelismo:

```text
transformar -> [carregar_csv, carregar_banco]
```

Se duas tarefas não dependem uma da outra, o orquestrador pode executá-las em paralelo, desde que existam recursos disponíveis.

---

## Apache Airflow

O **Apache Airflow** é uma plataforma open source para desenvolver, agendar, executar e monitorar workflows, especialmente pipelines de processamento em lote.

No Airflow, os fluxos são escritos em Python e representados por DAGs. Isso permite declarar explicitamente quais tarefas existem e quais dependências conectam essas tarefas.

A ideia principal é:

1. escrever a DAG em Python;
2. deixar o Airflow interpretar essa definição;
3. agendar e executar as tarefas;
4. registrar estado, logs e histórico de execução;
5. acompanhar tudo pela interface web.

### Entidades principais

**DAG**

Representa o fluxo completo. Define o agendamento, as tarefas e as dependências.

**Task**

Representa uma etapa do workflow. Deve ser pequena o bastante para ter logs, estado e falha compreensíveis.

**Operator**

Define o tipo de trabalho que uma task executa. No projeto, usamos o `PythonOperator`, que executa funções Python.

Exemplos de operators:

- `PythonOperator`;
- `BashOperator`;
- `HttpOperator`;
- `SQLExecuteQueryOperator`.

### Anatomia da DAG

No projeto da semana, a DAG importa as funções do pipeline:

```python
from pipeline_etl import extract, transform, load
```

Esse arquivo não é uma biblioteca externa. Ele é o script do próprio projeto, onde estão as funções do pipeline.

A DAG é configurada com parâmetros principais:

```python
with DAG(
    dag_id="pipeline_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(seconds=10),
    },
) as dag:
```

Principais parâmetros:

- `dag_id`: nome da DAG no Airflow;
- `start_date`: data a partir da qual o Airflow pode considerar execuções;
- `schedule`: frequência de execução;
- `catchup=False`: evita criar execuções antigas automaticamente;
- `retries`: número de novas tentativas quando uma task falha;
- `retry_delay`: tempo de espera entre as tentativas.

Cada função do pipeline vira uma task:

```python
extrair = PythonOperator(task_id="extrair", python_callable=extract)
transformar = PythonOperator(task_id="transformar", python_callable=transform)
carregar = PythonOperator(task_id="carregar", python_callable=load)
```

A dependência entre elas é declarada com:

```python
extrair >> transformar >> carregar
```

Isso significa que `transformar` só executa depois que `extrair` termina com sucesso, e `carregar` só executa depois que `transformar` termina com sucesso.

### Interface e monitoramento

A interface web do Airflow permite visualizar, executar e monitorar DAGs.

Duas visualizações importantes são:

- **Graph View:** mostra a estrutura lógica do pipeline.
- **Grid View:** mostra o comportamento da DAG ao longo do tempo.

Alguns estados importantes:

- `Scheduled`: pronta para entrar na fila;
- `Queued`: aguardando capacidade de execução;
- `Running`: tarefa em execução;
- `Success`: concluída com sucesso;
- `Failed`: terminou com erro;
- `Up for retry`: aguardando nova tentativa;
- `Skipped`: não foi executada por causa da lógica da DAG;
- `Upstream failed`: bloqueada porque uma dependência anterior falhou.

Quando ocorre uma falha, os logs da task são o primeiro lugar a verificar. O Airflow registra qual tarefa falhou, em qual execução e durante qual tentativa.

Retries ajudam em falhas temporárias, como instabilidade de rede. Eles não resolvem erros permanentes no código.

---

## Docker e Containers

O **Docker** é uma plataforma usada para criar, distribuir e executar aplicações em ambientes isolados e padronizados.

Um **container** é uma instância isolada criada a partir de uma imagem Docker. Ele executa uma aplicação com suas dependências e configurações, compartilhando o sistema operacional da máquina hospedeira.

O Airflow depende de vários componentes:

- interface web;
- scheduler;
- banco de metadados;
- dependências Python;
- diretórios de DAGs, scripts, dados e logs.

Com Docker, esses componentes são executados de forma padronizada, reduzindo diferenças entre máquinas e facilitando a reprodução do ambiente.

### Containers utilizados

No ambiente desta semana, são usados quatro serviços principais:

- **postgres:** banco de metadados do Airflow;
- **airflow-init:** inicializa o banco e cria o usuário inicial;
- **airflow-webserver:** disponibiliza a interface web em `localhost:8080`;
- **airflow-scheduler:** monitora as DAGs e executa as tasks.

O pipeline não precisa de um container separado. Ele roda dentro do ambiente do Airflow, pois a pasta `scripts/` é montada no container.

### Arquivos Docker

**`Dockerfile`**

Define a imagem usada pelo Airflow. Parte da imagem oficial do Airflow e instala as dependências do projeto.

Exemplo:

```dockerfile
FROM apache/airflow:2.10.5

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt
```

**`requirements.txt`**

Lista as bibliotecas Python adicionais usadas pelo pipeline:

```text
pandas==2.2.3
requests==2.32.3
```

**`docker-compose.yml`**

Define os serviços executados no ambiente local, seus volumes, portas e variáveis de ambiente.

Os volumes conectam pastas locais ao container:

- `./dags:/opt/airflow/dags`;
- `./scripts:/opt/airflow/scripts`;
- `./data:/opt/airflow/data`;
- `./logs:/opt/airflow/logs`.

O volume `postgres_data` preserva os metadados do Airflow mesmo quando os containers são parados.

---

## Prática da Semana

Nesta prática, o objetivo é orquestrar um pipeline ETL simples com Airflow e executar o ambiente local com Docker.

Os códigos de exemplo do pipeline (`pipeline_etl.py`) e da DAG (`pipeline_etl_dag.py`) estão disponíveis na pasta `códigos-exemplo`.

O pipeline deve estar organizado em um arquivo Python com três funções:

```python
def extract():
    ...

def transform():
    ...

def load():
    ...
```

No projeto da semana:

- `extract()` consulta a API DummyJSON e salva os dados brutos em JSON;
- `transform()` seleciona colunas, remove nulos e remove duplicatas;
- `load()` salva o resultado final em CSV local.

### Fonte de dados

A fonte de dados utilizada é a **DummyJSON**, uma API pública que disponibiliza dados fictícios para testes e exemplos de desenvolvimento.

Neste projeto, usamos o endpoint de produtos:

```text
https://dummyjson.com/products
```

Esse endpoint retorna uma lista de produtos com informações como:

- identificador do produto;
- nome;
- categoria;
- marca;
- preço;
- percentual de desconto;
- avaliação;
- quantidade em estoque.

Esses dados são úteis para a prática porque simulam uma fonte externa acessada via HTTP, permitindo demonstrar a etapa de extração com `requests` e a transformação dos registros com `pandas`.

### Procedimento resumido

1. Criar a estrutura do projeto:

```text
dags/
scripts/
data/
logs/
plugins/
```

2. Colocar o pipeline em:

```text
scripts/pipeline_etl.py
```

3. Criar a DAG em:

```text
dags/pipeline_etl_dag.py
```

4. Declarar as tasks da DAG:

```text
extrair -> transformar -> carregar
```

5. Criar os arquivos de ambiente:

```text
Dockerfile
requirements.txt
docker-compose.yml
.env
```

6. Subir o ambiente:

```bash
docker compose up --build
```

7. Acessar a interface do Airflow:

```text
http://localhost:8080
```

8. Ativar e executar a DAG:

```text
pipeline_etl
```

9. Acompanhar a execução pela `Grid View` e verificar os logs das tasks.

10. Conferir os arquivos gerados:

```text
data/dummyjson_products_raw.json
data/dummyjson_products.csv
```

### Comandos úteis

Parar os containers:

```bash
docker compose down
```

Parar e apagar os metadados do Airflow:

```bash
docker compose down -v
```

Ver logs:

```bash
docker compose logs -f
```

Executar o pipeline manualmente dentro do container:

```bash
docker compose exec airflow-scheduler python /opt/airflow/scripts/pipeline_etl.py
```
