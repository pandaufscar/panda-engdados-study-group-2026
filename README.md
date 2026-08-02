# 🐼 Panda UFSCar - Grupo de Estudos de Engenharia de Dados 2026

Este repositório apresenta a organização do grupo de estudos de **Engenharia de Dados** do Panda UFSCar em 2026.

A proposta do grupo é acompanhar o caminho percorrido pelos dados em sistemas reais: da coleta em arquivos, APIs e bancos, passando pela transformação, validação e modelagem, até a organização de pipelines executáveis e documentados.

Ao longo das semanas, os participantes constroem uma base prática para projetar fluxos de dados, lidar com problemas comuns de qualidade, integrar ferramentas e entender como componentes como PostgreSQL, Docker e Apache Airflow aparecem em uma arquitetura de dados.

---

## 📌 Competências Trabalhadas

O grupo busca desenvolver competências práticas em:

- leitura e escrita de dados em diferentes formatos;
- consumo de APIs e manipulação de respostas JSON;
- construção de pipelines ETL com Python e pandas;
- uso de SQL e PostgreSQL em fluxos de dados;
- modelagem relacional, dimensional e analítica;
- validação, qualidade, logging e tratamento de erros;
- orquestração de pipelines com Apache Airflow;
- execução local de ambientes com Docker;
- documentação e organização de projetos de dados.

---

## 🧭 Como o Grupo Está Organizado

O estudo é organizado em **10 semanas**, com progressão gradual e foco em entregas práticas.

As primeiras semanas apresentam os fundamentos e as principais fontes de dados. Em seguida, o grupo avança para bancos relacionais, modelagem, qualidade e orquestração. As últimas semanas são dedicadas à definição, implementação e finalização de um projeto completo.

Cada semana possui:

- conteúdo teórico sugerido;
- atividade prática;
- entrega relacionada ao tema.

O percurso foi planejado para que cada entrega semanal funcione como uma peça reutilizável no projeto final.

---

## 📅 Estrutura Semanal (Resumo)

**Semana 1 - Fundamentos de Engenharia de Dados**  
Papel do engenheiro de dados, ciclo de vida dos dados, visão geral de pipelines, introdução ao Python e à biblioteca pandas. A prática envolve configuração do ambiente, leitura de arquivos e exploração inicial de dados.

**Semana 2 - Fontes de Dados, APIs, ETL vs ELT**  
Estudo de fontes de dados, APIs REST, biblioteca `requests` e conceitos de ETL e ELT. A prática consiste em consumir uma API pública, tratar JSON com pandas e salvar dados brutos.

**Semana 3 - Bancos de Dados Relacionais e SQL**  
Introdução a bancos relacionais, tabelas, chaves, relacionamentos e SQL essencial. A prática envolve PostgreSQL, criação de tabelas, inserção de dados e consultas com Python.

**Semana 4 - Modelagem de Dados**  
Modelagem conceitual e lógica, diagramas ER, modelagem dimensional, tabelas fato e dimensão, e esquema estrela. A prática consiste em desenhar modelos para um domínio simples.

**Semana 5 - ETL/ELT Avançado, Qualidade e Logs**  
Modularização de pipelines, qualidade de dados, tratamento de nulos e duplicados, logging e tratamento de erros. A prática refatora o pipeline em funções e adiciona validações.

**Semana 6 - Orquestração e Apache Airflow**  
Introdução à orquestração de pipelines, conceito de DAG, Apache Airflow, tasks, dependências, retries e execução com Docker. A prática organiza o pipeline em `extract`, `transform` e `load`, criando uma DAG funcional no Airflow.

**Semana 7 - Data Warehouse e Modelagem Analítica**  
Diferenças entre Data Warehouse, Data Lake e Lakehouse, OLTP vs OLAP e modelagem analítica. A prática propõe o desenho da arquitetura final e um mockup de Data Warehouse.

**Semana 8 - Projeto Final: Definição**  
Definição de escopo, fonte de dados, requisitos, arquitetura, cronograma e divisão de tarefas do projeto final.

**Semana 9 - Projeto Final: Implementação**  
Implementação do pipeline completo, com tratamento de erros, logging, orquestração com Airflow e persistência em PostgreSQL.

**Semana 10 - Projeto Final: Finalização**  
Finalização das pendências, documentação do projeto, organização do repositório e preparação da entrega final.

---

## 🗂️ Como Navegar pelo Repositório

O material é separado por semana. Cada pasta concentra o conteúdo, as instruções e os artefatos relacionados ao tema correspondente:

```text
Semana 01/
Semana 02/
Semana 03/
...
Semana 8,9 e 10 - Projeto Final/
```

Dependendo do tema, uma semana pode conter:

- resumo teórico em Markdown;
- imagens e diagramas;
- códigos de exemplo.


---

## ⚙️ Funcionamento das Entregas

### Comunicação e acompanhamento

A comunicação será feita de forma assíncrona. Reuniões extraordinárias podem ocorrer quando necessário, mas o acompanhamento principal acontece por meio das entregas.

### Presença e entregas

A presença será contabilizada por meio das entregas das atividades práticas de cada semana.

As entregas devem ser enviadas no Google Drive dentro do prazo estipulado. Atividades atrasadas serão aceitas por até 3 semanas; após esse prazo, será aplicada falta na atividade correspondente.

### Tipos de entrega

Ao longo do grupo, as entregas podem incluir notebooks, scripts, prints de execução, diagramas, DAGs, documentação e partes do projeto final.

O objetivo é que cada entrega contribua para a construção progressiva de um repertório prático em Engenharia de Dados.

---


## 🚀 Projeto Final

O projeto final consolida os principais conceitos estudados ao longo do grupo. Cada integrante desenvolveu um pipeline de dados completo, escolhendo uma fonte de dados e um tema de interesse próprio.

A proposta do projeto é aplicar, em um repositório organizado, etapas como:

- extração de dados a partir de arquivos, APIs ou outras fontes;
- transformação, limpeza e validação dos dados;
- persistência dos dados em PostgreSQL;
- orquestração do pipeline com Apache Airflow;
- tratamento de erros e logging;
- documentação do funcionamento do pipeline;
- organização do código para facilitar reprodução e manutenção.

Outros componentes trabalhados durante o ciclo, como Docker, validações e logging, devem ser utilizados conforme a necessidade de cada projeto.

### Projetos desenvolvidos

| Integrante | Projeto | Repositório |
|-----------|---------|-------------|
| Adriano Tavares | Pipeline ETL Climabr | [climabr-pipeline](https://github.com/aatsac/climabr-pipeline) |
| Annalice Fernandes dos Santos | Pipeline SP Trans | [sptrans-pipeline](https://github.com/Annalicefs/sptrans-pipeline) |
| Gabriela Guerra | Pipeline Biodiversidade | [pipeline-biodiversidade-gbif](https://github.com/hub-gabrielaguerra/pipeline-biodiversidade-gbif) |
| Julia Tavares dos Santos | Pipeline Pokémon | [pokemon-pipeline](https://github.com/JuuJxp/pokemon-pipeline) |
| Lucas Nacaguma | Pipeline de Monitoramento Meteorológico | [monitoramento-meteorologico](https://github.com/LucasNacaguma/monitoramento-meteorol-gico) |
| Sérgio Felipe Bezerra Rabelo | Pipeline BCB Pix | [bcb-pix-pipeline](https://github.com/felipebrabelo/bcb-pix-pipeline) |
| Vinicius Matheus Blanco | Pipeline Vagas Tech | [pipeline-vagas-tech](https://github.com/ViniMBlanco/pipeline-vagas-tech) |
