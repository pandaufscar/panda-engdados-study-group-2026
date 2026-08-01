# Data Warehouse e Modelagem Analítica

**Grupo PANDA · Engenharia de Dados — Semana 7**

Nas semanas anteriores, vimos como extrair dados de diferentes fontes, tratá-los em pipelines e persisti-los em bancos relacionais. Chegou a hora de dar um passo além: entender **onde e como esses dados devem viver** quando o objetivo é análise, e não apenas operação do dia a dia. É isso que este material cobre, as diferentes formas de armazenar dados em escala, a diferença entre sistemas transacionais e analíticos, e a técnica de modelagem que sustenta praticamente todo Data Warehouse do mercado: o esquema estrela.

---

## 1. Por que existem tantas formas de armazenar dados?

Se você já ouviu falar em Data Warehouse, Data Lake e Data Lakehouse e ficou com a sensação de que são só sinônimos com nomes diferentes, vale entender que cada um surgiu para resolver um problema de uma época distinta.

Nos anos 80 e 90, as empresas precisavam consolidar dados vindos de vários sistemas transacionais para gerar relatórios gerenciais. A resposta foi o **Data Warehouse**: um repositório de dados estruturados, tratados e modelados *antes* de serem carregados, o que chamamos de **schema-on-write**.

Já nos anos 2010, o volume, a variedade e a velocidade dos dados explodiram (o fenômeno do Big Data). Passou a ser inviável tratar tudo antes de guardar, então surgiu o **Data Lake**: um repositório que aceita dados brutos, em qualquer formato, aplicando o esquema apenas no momento da leitura, o **schema-on-read**.

Mais recentemente, nos anos 2020, as empresas perceberam que precisavam de BI tradicional e de Machine Learning rodando sobre a mesma base de dados, sem duplicar tudo em duas plataformas diferentes. Surge o **Data Lakehouse**, que tenta unir a flexibilidade do lake com a governança do warehouse.

Essas três abordagens coexistem hoje. Nenhuma "venceu" a outra, a escolha depende do caso de uso, do orçamento e da maturidade de dados da empresa.

---

## 2. Data Warehouse, Data Lake e Data Lakehouse

### 2.1 Data Warehouse

Repositório centralizado de dados **estruturados**, já tratados e otimizados para consultas analíticas e geração de relatórios. Como o esquema é definido antes da carga, todo dado passa por um processo de ETL (Extract, Transform, Load) que padroniza e valida as informações antes delas chegarem ao warehouse.

**Vantagens:** consultas rápidas e previsíveis, forte governança e qualidade de dados, facilidade de uso para áreas de negócio.

**Limitações:** rígido a mudanças de esquema, custo mais alto para grandes volumes, pouco eficiente para dados não estruturados.

**Exemplo de uso:** relatórios financeiros mensais, dashboards executivos de vendas.

### 2.2 Data Lake

Repositório que guarda grandes volumes de dados em seu formato bruto e nativo, estruturado, semiestruturado ou não estruturado, sem exigir estrutura prévia. O esquema só é aplicado na leitura (**schema-on-read**), o que dá bastante flexibilidade, mas exige disciplina para não virar aquilo que o mercado chama de "pântano de dados" (um amontoado de arquivos sem organização nem confiabilidade).

**Vantagens:** grande flexibilidade de formatos, custo de armazenamento reduzido, ideal para explorar dados antes de decidir como modelá-los.

**Limitações:** risco de perda de governança, performance de consulta inferior à de um warehouse, exige mais preparo antes de qualquer análise.

**Exemplo de uso:** armazenamento de logs de aplicação, imagens, dados de sensores IoT.

### 2.3 Data Lakehouse

Arquitetura que combina a flexibilidade do Data Lake com a governança e a performance do Data Warehouse, através de uma camada de metadados e transações ACID sobre um armazenamento de objetos. Tecnologias como **Delta Lake**, **Apache Iceberg** e **Apache Hudi** são o que viabilizam essa combinação na prática.

**Vantagens:** um único ponto de verdade para os dados, elimina a duplicação entre lake e warehouse, governança superior à de um lake puro.

**Limitações:** tecnologia mais recente e ainda em maturação, pode exigir mudança cultural na equipe.

**Exemplo de uso:** empresas que precisam de BI e Machine Learning sobre a mesma base de dados.

### 2.4 Comparativo resumo

| Critério | Data Warehouse | Data Lake | Data Lakehouse |
|---|---|---|---|
| Tipo de dado | Estruturado | Todos os tipos (bruto) | Todos os tipos |
| Esquema | Schema-on-write | Schema-on-read | Flexível, com governança |
| Custo de armazenamento | Mais alto | Baixo | Baixo a médio |
| Performance de consulta | Alta | Baixa a média | Alta |
| Uso principal | BI e relatórios | Ciência de dados, ML | BI e ML unificados |
| Exemplo de tecnologia | Amazon Redshift | Amazon S3, HDFS | Databricks, Delta Lake |

---

## 3. OLTP vs OLAP

Outra distinção fundamental é entre dois **perfis de processamento** de dados: OLTP e OLAP. Não são bancos de dados diferentes por si só, mas sim formas diferentes de organizar e consultar os dados, de acordo com o objetivo do sistema.

**OLTP (Online Transaction Processing)** sustenta as operações do dia a dia de uma aplicação: inserir, atualizar e excluir registros. Precisa lidar com alta concorrência, muitas transações curtas acontecendo ao mesmo tempo, e por isso os dados costumam estar normalizados, priorizando consistência e integridade.

**OLAP (Online Analytical Processing)** é voltado para consultas analíticas complexas, com predomínio de leitura. Os dados costumam estar desnormalizados, seguindo o esquema estrela (que veremos na seção 4), priorizando desempenho de agregações em vez de velocidade de escrita.

| Aspecto | OLTP | OLAP |
|---|---|---|
| Estrutura de dados | Normalizado (3FN) | Desnormalizado (esquema estrela) |
| Tipo de operação | `INSERT` / `UPDATE` / `DELETE` frequentes | `SELECT` com agregações complexas |
| Tempo de resposta esperado | Milissegundos | Segundos a minutos |
| Volume por operação | Poucos registros por transação | Milhões de registros por consulta |
| Usuários típicos | Aplicações operacionais | Analistas de dados, gestores |

Um exemplo prático ajuda a fixar a diferença. No dia a dia de um sistema de vendas (OLTP), uma transação comum seria:

```sql
UPDATE pedido SET status = 'pago' WHERE id_pedido = 1001;
```

Já num relatório analítico (OLAP), a consulta típica agrega muitos registros de uma vez:

```sql
SELECT MONTH(data_pedido) AS mes, SUM(valor_total) AS faturamento
FROM fato_vendas
GROUP BY MONTH(data_pedido);
```

Repare que a segunda consulta não faria sentido rodando direto sobre um banco OLTP de produção: ela varreria milhões de linhas normalizadas, com múltiplos `JOIN`s, competindo por recursos com as transações do sistema. É exatamente esse problema que a modelagem analítica, vista a seguir, resolve.

---

## 4. Modelagem Analítica: o Esquema Estrela

A modelagem analítica organiza o Data Warehouse para que consultas fiquem simples, rápidas e fáceis de entender, mesmo para quem não é técnico. A técnica mais usada para isso é o **esquema estrela**: uma tabela **fato** central, conectada diretamente a várias tabelas **dimensão**.

### 4.1 Tabela fato

É a tabela central do esquema: guarda as **métricas numéricas** (também chamadas de *measures*) e as **chaves estrangeiras** que apontam para cada dimensão relacionada ao evento de negócio.

```
fato_vendas
├── id_produto   FK -> dim_produto
├── id_cliente   FK -> dim_cliente
├── id_tempo     FK -> dim_tempo
├── id_loja      FK -> dim_loja
├── quantidade   INT
└── valor_total  DECIMAL(10,2)
```

Existem três tipos de fatos, e vale saber diferenciá-los:

- **Aditivos** — podem ser somados em qualquer dimensão (ex.: valor de uma venda).
- **Semi-aditivos** — somam em alguns eixos, mas não em todos (ex.: saldo em conta, que pode ser somado entre contas, mas não ao longo do tempo).
- **Não-aditivos** — não fazem sentido somados (ex.: uma taxa percentual).

O ponto mais importante ao modelar uma fato é decidir sua **granularidade**: o que exatamente representa cada linha. Veremos isso com um exemplo na seção 5.

### 4.2 Tabelas dimensão

Descrevem o **contexto** dos fatos — quem, o quê, quando e onde — e costumam conter atributos organizados em hierarquias, como em `dim_tempo` (dia → mês → trimestre → ano) ou `dim_produto` (item → subcategoria → categoria).

```
dim_produto
├── id_produto     INT (PK)
├── nome           VARCHAR
├── categoria      VARCHAR
├── subcategoria   VARCHAR
└── marca          VARCHAR
```

Um detalhe importante: dimensões costumam ser **desnormalizadas de propósito**. Repetir texto descritivo custa pouco espaço em disco e evita *joins* extras nas consultas analíticas, o oposto do que faríamos num banco OLTP.

### 4.3 Slowly Changing Dimensions (SCD)

Dimensões mudam ao longo do tempo, um cliente muda de cidade, um produto muda de categoria. A forma como tratamos essa mudança tem nome: **Slowly Changing Dimensions**.

| Tipo | Comportamento | Efeito no histórico |
|---|---|---|
| Tipo 1 | Sobrescreve o valor antigo | Perde o histórico |
| Tipo 2 | Cria uma nova linha a cada mudança | Mantém o histórico completo |
| Tipo 3 | Guarda o valor anterior em outra coluna | Mantém só a mudança mais recente |

A escolha do tipo de SCD depende de uma pergunta simples: você precisa saber como era o dado *no momento do evento*, ou só o dado mais atualizado já basta?

### 4.4 Visualizando o esquema estrela

```
                dim_cliente
                     |
dim_tempo — fato_vendas — dim_produto
                     |
                 dim_loja
```

O nome "estrela" vem justamente disso: a fato no centro, com as dimensões ao redor, conectadas diretamente, sem tabelas intermediárias. Isso significa que qualquer consulta precisa de **apenas um join** entre a fato e cada dimensão relevante, o que é simples e rápido para ferramentas de BI.

### 4.5 Esquema estrela vs. esquema floco de neve (snowflake)

Existe uma variação do esquema estrela chamada **floco de neve**, em que as dimensões são normalizadas em subtabelas, por exemplo, separando `categoria` para fora de `dim_produto`.

| | Esquema Estrela | Esquema Floco de Neve |
|---|---|---|
| Estrutura das dimensões | Totalmente desnormalizadas | Normalizadas em subtabelas |
| Quantidade de tabelas | Menor | Maior |
| Complexidade das consultas | Menor (menos *joins*) | Maior (mais *joins*) |
| Espaço em disco | Mais redundância | Menos redundância |
| Velocidade de consulta | Mais rápida | Um pouco mais lenta |

Com o custo de armazenamento cada vez mais barato, o esquema estrela costuma ser preferido na maioria dos projetos atuais, a economia de espaço do floco de neve raramente compensa a complexidade extra nas consultas.

---

## 5. Granularidade na prática

Granularidade é o nível de detalhe que cada linha da tabela fato representa, e ela precisa ser decidida **antes** de desenhar as tabelas, não depois.

Imagine que o pedido `#1001` tenha três itens diferentes. Se a granularidade for **por pedido**, a fato teria uma única linha:

| id_pedido | cliente | valor_total |
|---|---|---|
| 1001 | Ana | R$ 300,00 |

Isso é compacto, mas não permite saber quais produtos foram vendidos. Se a granularidade for **por item do pedido**, a mesma informação vira três linhas:

| id_pedido | produto | qtd | valor |
|---|---|---|---|
| 1001 | Fone BT | 1 | R$ 150,00 |
| 1001 | Cabo USB | 2 | R$ 50,00 |
| 1001 | Capa | 1 | R$ 100,00 |

O trade-off é direto: granularidade mais fina permite análises mais profundas (ex.: qual produto vende mais), mas gera mais linhas. Granularidade mais grossa é mais compacta, mas perde detalhe. A regra prática para decidir: **comece pela pergunta de negócio que o Data Warehouse precisa responder**, a granularidade certa geralmente cai naturalmente dessa pergunta.

---

## 6. Exemplo aplicado: e-commerce

Juntando os conceitos das seções 4 e 5, veja como ficaria o esquema estrela de uma loja virtual:

```
                dim_cliente
                     |
dim_tempo — fato_pedidos — dim_produto
                     |
               dim_pagamento
```

- **fato_pedidos** — granularidade por item de pedido, com as medidas `quantidade`, `valor_unitário` e `valor_total`.
- **dim_cliente** — dados do comprador.
- **dim_produto** — categoria, marca, subcategoria.
- **dim_tempo** — dia, mês, ano.
- **dim_pagamento** — forma de pagamento utilizada.

Com esse modelo montado, é possível responder perguntas de negócio que seriam lentas ou inviáveis num banco puramente transacional, como: *"Qual categoria de produto vendeu mais no último trimestre, por forma de pagamento?"*

---

## 7. Cloud Computing e ferramentas de mercado

### 7.1 Cloud computing (opcional)

Boa parte dos Data Warehouses modernos roda hoje sobre infraestrutura de nuvem: acesso a computação, armazenamento e rede sob demanda, pela internet, sem precisar manter hardware próprio. Existem três modelos de serviço:

- **IaaS** (Infrastructure as a Service) — servidores e redes virtuais.
- **PaaS** (Platform as a Service) — um ambiente pronto para rodar aplicações.
- **SaaS** (Software as a Service) — uma aplicação já pronta para uso.

Os principais provedores são AWS, Microsoft Azure e Google Cloud Platform. A vantagem para Data Warehouse é clara: soluções gerenciadas eliminam a necessidade de infraestrutura própria, escalam sob demanda e costumam ser cobradas por uso, reduzindo o custo inicial de um projeto.

### 7.2 Ferramentas de mercado

| Ferramenta | Categoria | Descrição |
|---|---|---|
| Amazon Redshift | Data Warehouse | Gerenciado pela AWS, otimizado para consultas analíticas em larga escala |
| Google BigQuery | Data Warehouse | Serverless, cobrança por consulta processada |
| Snowflake | Data Warehouse multi-cloud | Separa armazenamento e processamento de forma independente |
| Databricks | Lakehouse | Baseado em Apache Spark e Delta Lake, forte em BI e Machine Learning |
| Azure Synapse Analytics | DW + Big Data | Integra as duas frentes numa única plataforma da Microsoft |

Vale sempre consultar a documentação oficial de cada ferramenta antes de adotá-la num projeto real, o mercado evolui rápido e novas versões trazem mudanças frequentes.

---

## 8. Boas práticas (resumo)

- Defina a **granularidade** da tabela fato antes de desenhar qualquer tabela.
- Documente as **regras de negócio** de cada métrica junto com o time que solicitou o dado.
- Mantenha ambientes **OLTP e OLAP separados** — nunca use a mesma tabela para os dois propósitos.
- Escolha o tipo de **SCD** adequado para cada dimensão, de acordo com a necessidade real de histórico.
- Automatize **testes de qualidade de dados** (nulos, duplicados, tipos) antes de qualquer carga no Data Warehouse.
- Prefira o **esquema estrela** ao floco de neve, a menos que a economia de espaço seja realmente crítica.

---

## 9. Glossário

| Termo | Definição |
|---|---|
| **Data Warehouse** | Repositório centralizado de dados estruturados e tratados, otimizado para consultas analíticas |
| **Data Lake** | Repositório de dados brutos, em qualquer formato, sem esquema definido previamente |
| **Data Lakehouse** | Arquitetura que une a flexibilidade do lake com a governança do warehouse |
| **Schema-on-write** | O esquema é definido antes da carga dos dados |
| **Schema-on-read** | O esquema é aplicado apenas no momento da leitura dos dados |
| **OLTP** | Processamento otimizado para transações do dia a dia (inserir, atualizar, excluir) |
| **OLAP** | Processamento otimizado para consultas analíticas e agregações |
| **Esquema estrela** | Modelo com uma tabela fato central conectada diretamente a tabelas dimensão |
| **Esquema floco de neve** | Variação do esquema estrela com dimensões normalizadas em subtabelas |
| **Tabela fato** | Tabela central que armazena métricas numéricas e chaves para as dimensões |
| **Tabela dimensão** | Tabela que descreve o contexto de um fato (quem, o quê, quando, onde) |
| **Granularidade** | Nível de detalhe representado por cada linha da tabela fato |
| **SCD (Slowly Changing Dimension)** | Estratégia para tratar mudanças de valor em uma dimensão ao longo do tempo |
| **ETL** | Extract, Transform, Load — processo de extrair, tratar e carregar dados |
| **ACID** | Conjunto de garantias de transação: Atomicidade, Consistência, Isolamento e Durabilidade |
| **IaaS / PaaS / SaaS** | Modelos de serviço em nuvem: infraestrutura, plataforma e software, respectivamente |

---

## 10. Materiais complementares

- IBM Think — [Data Warehouse vs Data Lake vs Data Lakehouse](https://www.ibm.com/br-pt/think/topics/data-warehouse-vs-data-lake-vs-data-lakehouse)
- Databricks — [Data Lakes vs Data Warehouses](https://www.databricks.com/br/blog/data-lakes-vs-data-warehouses-what-your-organization-needs-know)
- AWS — [The Difference Between OLAP and OLTP](https://aws.amazon.com/pt/compare/the-difference-between-olap-and-oltp/)
- GeeksforGeeks — [Difference between OLAP and OLTP in DBMS](https://www.geeksforgeeks.org/dbms/difference-between-olap-and-oltp-in-dbms/)
- Insper Data Engineering — [Data Warehouse](https://insper.github.io/dataeng/classes/03-data-warehouse/intro/)
- GeeksforGeeks — [Data Warehousing Tutorial](https://www.geeksforgeeks.org/dbms/data-warehousing-tutorial/)
- IBM Think — [Cloud Computing](https://www.ibm.com/br-pt/think/topics/cloud-computing)

---

## 11. Atividade da semana

A prática desta semana não envolve código, o foco é **arquitetura e modelagem**. A entrega consiste em:

1. **Diagrama de arquitetura final** de um domínio de dados escolhido pelo grupo, cobrindo o fluxo completo: fontes de dados → ingestão → armazenamento (Data Lake/staging) → transformação → Data Warehouse → consumo (BI/dashboards).
2. **Mockup do Data Warehouse** para esse domínio: definição da tabela fato, das dimensões e da granularidade, seguindo o esquema estrela (ou floco de neve, se fizer sentido para alguma dimensão específica).

O ponto de partida recomendado é sempre a pergunta de negócio que o Data Warehouse precisa responder, a granularidade e as dimensões saem naturalmente dela.