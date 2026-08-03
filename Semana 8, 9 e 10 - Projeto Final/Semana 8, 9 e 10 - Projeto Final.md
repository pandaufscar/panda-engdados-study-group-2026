# Semanas 8, 9 e 10 - Projeto Final

**Grupo PANDA · Engenharia de Dados**

Nas semanas anteriores, foram apresentados os principais componentes de um fluxo de Engenharia de Dados: leitura e escrita de arquivos, consumo de APIs, ETL, bancos relacionais, modelagem de dados, qualidade, logs, tratamento de erros, orquestração com Airflow e conceitos de Data Warehouse.

As semanas 8, 9 e 10 são dedicadas ao **projeto final**, que tem como objetivo consolidar esses conceitos em um pipeline de dados completo, funcional e documentado.

O projeto deve ser desenvolvido individualmente. Cada participante deve escolher uma API como fonte de dados, aplicar etapas de extração, transformação e carga, persistir os dados em PostgreSQL e utilizar Airflow para orquestrar a execução do pipeline.

---

## Objetivos do Projeto Final

Ao final do projeto, espera-se que o participante consiga:

- definir uma API adequada para um pipeline;
- planejar a arquitetura geral da solução;
- implementar um pipeline ETL modular;
- aplicar tratamento de nulos, duplicados e inconsistências;
- persistir os dados em PostgreSQL;
- orquestrar o pipeline com Apache Airflow;
- registrar logs e tratar falhas comuns;
- organizar o repositório de forma reprodutível;
- documentar corretamente o repositório para reprodução.

---

## Requisitos do Projeto

O projeto final deve conter, no mínimo:

- uma API definida como fonte de dados;
- um pipeline Python organizado em funções ou módulos;
- uma etapa de **extração** dos dados;
- uma etapa de **transformação**, com limpeza e padronização;
- uma etapa de **carga**;
- persistência dos dados em **PostgreSQL**;
- orquestração com **Apache Airflow**;
- tratamento de erros e logging;
- documentação no `README.md`;
- instruções claras de execução.

Quando fizer sentido para o projeto, também é recomendado incluir:

- Docker ou Docker Compose para facilitar a execução;
- validações de qualidade;
- modelo relacional ou diagrama simples;
- arquivos de exemplo ou dados de teste.

---

## Estrutura Recomendada do Repositório

Cada projeto pode adaptar sua estrutura, mas uma organização recomendada é:

```text
.
├── dags/
│   └── pipeline_dag.py
├── scripts/
│   └── pipeline.py
├── data/
├── docs/
├── logs/
├── requirements.txt
└── README.md
```

### Sugestão de responsabilidades

| Caminho | Responsabilidade |
|---|---|
| `dags/` | Arquivos de DAG do Airflow |
| `scripts/` | Código principal do pipeline |
| `data/` | Dados brutos, intermediários ou exportados, quando aplicável |
| `docs/` | Diagramas, prints e documentação complementar |
| `logs/` | Logs locais, quando forem persistidos em arquivo |
| `requirements.txt` | Dependências Python |
| `README.md` | Explicação do projeto e instruções de execução |

O uso de Docker é opcional para o projeto final. O Airflow pode ser executado localmente com instalação via `pip`, por exemplo com `pip install apache-airflow`.

---

## Semana 8 - Definição do Projeto

A Semana 8 é dedicada ao planejamento. Antes de implementar, é importante definir com clareza o que será construído.

Nesta etapa, o participante deve escolher uma API como fonte de dados e descrever o escopo do projeto.

### Pontos a definir

- Qual é o tema do projeto?
- Qual API será utilizada?
- Qual é a breve descrição da API e dos dados retornados?
- Quais dados serão extraídos?
- Quais são os requisitos do projeto?
- Quais transformações serão necessárias?
- Onde os dados serão persistidos?
- Quais tabelas devem existir no PostgreSQL?
- Como o pipeline será executado pelo Airflow?

### Escopo

O escopo deve ser pequeno o suficiente para ser implementado até a Semana 10, mas completo o bastante para demonstrar um fluxo real de Engenharia de Dados.

Um bom escopo deve deixar claro:

- objetivo do pipeline;
- origem dos dados;
- destino dos dados;
- frequência ou forma de execução;
- principais campos utilizados;
- transformações esperadas;
- resultado final esperado.

### Entrega da Semana 8

A entrega deve conter um documento de escopo em pdf ou README em Markdown com:

- tema do projeto;
- API escolhida como fonte de dados;
- requisitos do projeto;
- esboço da arquitetura proposta.

---

## Semana 9 - Implementação do Projeto

A Semana 9 é dedicada à construção da primeira versão funcional do pipeline.

Nesta etapa, o foco é fazer o fluxo principal funcionar de ponta a ponta: extrair os dados, transformá-los, persisti-los em PostgreSQL e executar o processo com Airflow.

### Pipeline ETL

O pipeline deve ser modular. Uma estrutura simples pode conter:

```python
def extract():
    ...

def transform():
    ...

def load():
    ...
```

Cada função deve ter uma responsabilidade clara:

- `extract()`: obter os dados da fonte;
- `transform()`: limpar, padronizar e validar os dados;
- `load()`: persistir os dados tratados no PostgreSQL.

### Persistência em PostgreSQL

O projeto deve criar ou utilizar tabelas no PostgreSQL para armazenar os dados processados.

Alguns pontos importantes:

- definir nomes claros para tabelas e colunas;
- escolher tipos de dados adequados;
- evitar inserir dados duplicados;
- registrar quando os dados foram coletados ou processados, se fizer sentido;
- documentar como acessar ou recriar o banco.

### Orquestração com Airflow

O pipeline deve ser executado por uma DAG do Airflow.

Um fluxo mínimo esperado é:

```text
extrair -> transformar -> carregar
```

A DAG deve declarar as dependências entre as etapas e permitir acompanhar a execução pela interface do Airflow.

Também é recomendado configurar:

- `dag_id`;
- `start_date`;
- `schedule`;
- `catchup`;
- `retries`;
- `retry_delay`.

### Logs e tratamento de erros

Logging e tratamento de erros são parte obrigatória do projeto. O pipeline deve facilitar a identificação de falhas desde a primeira implementação.

Boas práticas:

- registrar início e fim de cada etapa;
- registrar quantidade de registros processados;
- tratar erros de requisição, leitura ou escrita;
- exibir mensagens úteis nos logs;
- evitar falhas silenciosas.

### Entrega da Semana 9

A entrega deve conter:

- código inicial do pipeline;
- conexão funcional com PostgreSQL;
- DAG criada no Airflow;
- README parcialmente preenchido com instruções de execução.

---

## Semana 10 - Finalização e Documentação

A Semana 10 é dedicada aos ajustes finais, organização do repositório e documentação do projeto.

Nesta etapa, o pipeline deve estar funcional e o repositório deve estar compreensível para outra pessoa executar ou avaliar.

### Checklist de finalização

Antes da entrega final, verifique se o projeto possui:

- API utilizada documentada;
- pipeline executando sem intervenção manual;
- funções ou módulos bem separados;
- carga dos dados em PostgreSQL;
- DAG funcional no Airflow;
- instruções de instalação e execução;
- dependências listadas;
- logs ou mensagens de execução;
- tratamento de erros principais;
- README atualizado.

### Entrega da Semana 10

A entrega final deve conter:

- repositório organizado;
- pipeline completo;
- DAG funcional;
- persistência em PostgreSQL;
- documentação de uso.

---

## Observações Finais

O projeto final não precisa ser grande. Um pipeline pequeno, bem organizado, executável e documentado é mais adequado do que uma solução muito ampla e difícil de reproduzir.

Comece pelo pipeline funcionando de ponta a ponta, mesmo que simples. Refinamentos podem ser feitos depois que o fluxo principal estiver executando.

O objetivo principal é demonstrar domínio do fluxo completo:

```text
API -> extração -> transformação -> PostgreSQL -> Airflow -> documentação
```

