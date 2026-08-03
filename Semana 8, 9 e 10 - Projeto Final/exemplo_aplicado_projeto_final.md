# Câmbio em Dia — Projeto Integrador do Minicurso

O **Câmbio em Dia** é o projeto final do minicurso de Engenharia de Dados. Ele foi pensado para conectar, em uma única solução, os conceitos estudados ao longo das semanas: coletar um dado externo, tratá-lo, garantir sua qualidade, armazená-lo e deixá-lo pronto para análise.

O projeto usa cotações oficiais PTAX do Banco Central do Brasil para construir uma série histórica de moedas como dólar, euro e libra em relação ao real.

## A ideia do projeto

O pipeline consulta a API PTAX, trata as cotações e as disponibiliza de forma organizada. Com os dados prontos, será possível responder perguntas como:

- Como variou a cotação de uma moeda em determinado período?
- Qual foi a maior diferença entre cotação de compra e venda?
- Quais registros apresentaram problemas de qualidade?

```text
API PTAX → extração → transformação → validação → armazenamento → análise
```

## Como o projeto conecta o minicurso

| Semana | O que foi estudado | Onde aparece no Câmbio em Dia |
| --- | --- | --- |
| 1 | Python e pandas | Leitura da configuração das moedas, manipulação dos dados e criação de colunas como data de coleta e `spread`. |
| 2 | APIs, JSON, ETL e ELT | Consulta à API PTAX, recebimento do JSON e organização do fluxo de extrair, transformar e carregar. |
| 3 | PostgreSQL e SQL | Persistência das cotações e consultas sobre o histórico armazenado. |
| 4 | Modelagem de dados | Definição das entidades do domínio de câmbio e preparação das tabelas. |
| 5 | Qualidade, logs e tratamento de erros | Verificação de dados obrigatórios, valores inválidos, duplicidades, falhas por moeda e registros de auditoria. |
| 6 | Apache Airflow e Docker | Agendamento e monitoramento da pipeline por uma DAG, em ambiente reproduzível com containers. |
| 7 | Data Warehouse e modelagem analítica | Organização das cotações em modelo estrela para consultas por data, moeda e fonte. |

## Fluxo de ponta a ponta

```text
config/moedas.json
        │
        ▼
API PTAX do Banco Central
        │
        ▼
Extract → Transform → Validate → Load
                                  ├── PostgreSQL
                                  ├── CSV diário
                                  └── Logs
        │
        ▼
Data Warehouse → consultas e análises
```

A configuração permite ativar ou desativar moedas sem alterar o código. Cada moeda é processada individualmente, para que uma falha isolada não interrompa a coleta das demais. A carga será idempotente: executar novamente a mesma data não deve criar registros duplicados.

## Resultado esperado

Ao final, o projeto demonstrará a jornada completa da Engenharia de Dados:

1. consumir uma fonte de dados pública;
2. transformar dados brutos em informações estruturadas;
3. validar e registrar problemas de qualidade;
4. armazenar os dados de forma confiável;
5. orquestrar a execução;
6. disponibilizar uma base para análise histórica.

Por isso, o Câmbio em Dia não é apenas um exemplo de ETL: é a aplicação prática de todos os principais conteúdos do minicurso em um único pipeline.

Para os detalhes técnicos da proposta, consulte o [README principal](README.md).
