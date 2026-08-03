# Semana 4 — Modelagem de Dados: Do Transacional ao Analítico

Nesta semana, o objetivo é compreender a jornada do dado desde a sua captura nas aplicações operacionais até a sua estruturação para análises de negócios. A modelagem de dados não é uma ciência exata de tamanho único; ela muda drasticamente dependendo de **como** os dados serão consumidos. 

Além da teoria estrutural, a prática consiste em desenhar modelos para um domínio de e-commerce utilizando "Diagramas como Código".

## Objetivos de aprendizagem

- Diferenciar a arquitetura e os objetivos de sistemas OLTP e OLAP.
- Compreender os fundamentos da Modelagem Entidade-Relacionamento (ER).
- Dominar os conceitos de Chaves (Primária, Estrangeira e Surrogate).
- Entender o propósito da modelagem dimensional (Data Warehouses).
- Classificar, projetar e relacionar Tabelas Fato e Tabelas Dimensão.
- Diferenciar os esquemas Estrela (*Star Schema*) e Floco de Neve (*Snowflake*).
- Gerar representações visuais dos modelos utilizando a biblioteca `graphviz` em Python.

---

## 1. O Ciclo de Vida do Dado: OLTP vs. OLAP

Antes de desenhar qualquer tabela, o engenheiro de dados precisa perguntar: *"Esse banco vai suportar o aplicativo rodando em tempo real ou vai suportar o painel do time de negócios?"*

| Característica | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
|---|---|---|
| **Objetivo** | Processar transações diárias do negócio. | Suportar tomada de decisão e BI. |
| **Padrão de Leitura** | Lê e escreve poucas linhas por vez. | Lê milhões de linhas simultaneamente. |
| **Modelagem** | Relacional (Diagrama ER). Altamente normalizado (evita redundância). | Dimensional (Fato/Dimensão). Desnormalizado (aceita redundância para ganhar velocidade). |
| **Métrica de Sucesso**| Velocidade de *Insert/Update*, integridade do dado. | Velocidade de resposta para *Queries* complexas (Agregações, `GROUP BY`). |

> **O Elo de Ligação:** Os dados nascem no OLTP (ex: o banco do aplicativo da loja). Para chegarem ao OLAP (o Data Warehouse), eles passam por processos de Extração, Transformação e Carga (Pipelines de **ETL/ELT**).

## 2. Modelagem Entidade-Relacionamento (ER)

Focada no mundo OLTP, a modelagem ER garante que o banco de dados seja um reflexo fiel das regras de negócio. 

### Elementos Fundamentais
* **Entidades:** Objetos de negócio sobre os quais queremos guardar dados (ex: `Cliente`, `Pedido`).
* **Atributos:** Detalhes das entidades (ex: `Nome`, `CPF`, `Data_Compra`).
* **Relacionamentos e Cardinalidade:** Como as entidades interagem. 
  * **1:1 (Um para Um):** Um usuário tem um único carrinho de compras ativo.
  * **1:N (Um para Muitos):** Um cliente pode fazer vários pedidos, mas um pedido pertence a apenas um cliente. *(O mais comum).*
  * **N:M (Muitos para Muitos):** Um pedido pode ter vários produtos, e um produto pode estar em vários pedidos. *(Exige a criação de uma tabela intermediária).*

### Identidade: O papel das Chaves
Para que o relacionamento funcione no banco de dados físico, utilizamos chaves:
* **Chave Primária (PK):** O identificador único de uma linha dentro de uma tabela. Nunca se repete e não pode ser nulo.
* **Chave Estrangeira (FK):** Uma coluna em uma tabela que faz referência à Chave Primária de outra tabela. É ela que cria o "link" entre os dados.

## 3. O Mundo de Analytics: Modelagem Dimensional

Quando movemos os dados para o Data Warehouse (OLAP), abandonamos as regras rígidas de normalização em favor da **performance de leitura**. Aqui, dividimos o mundo em duas categorias de tabelas.

### Tabelas Fato
Guardam os eventos que aconteceram no negócio. Elas crescem rapidamente de forma vertical (muitas linhas).
* **O que contêm:** Métricas quantitativas (quantidades, valores, descontos) e as Chaves Estrangeiras (FKs).
* **Exemplo:** `Fato_Vendas`, `Fato_Cliques_Site`, `Fato_Movimentacao_Estoque`.

### Tabelas Dimensão
Fornecem o contexto para os fatos. Ajudam a responder *Quem, O que, Onde, Quando e Por quê*. Elas crescem horizontalmente (muitas colunas detalhadas).
* **O que contêm:** Atributos descritivos de texto (nomes, categorias, regiões).
* **Exemplo:** `Dim_Cliente`, `Dim_Produto`, `Dim_Tempo`.

### Star Schema vs. Snowflake
* **Esquema Estrela (Star Schema):** Uma Tabela Fato central conectada diretamente a várias Dimensões desnormalizadas. Excelente para performance, pois exige apenas 1 nível de `JOIN`.
* **Esquema Floco de Neve (Snowflake):** As Tabelas Dimensão são normalizadas (ex: A `Dim_Produto` se liga a uma `Dim_Categoria`). Economiza espaço em disco, mas exige múltiplos `JOINs`, deixando as consultas mais lentas.

## 4. Prática: Diagramas como Código (graphviz)

Para documentar nossa modelagem sem depender de ferramentas visuais pagas ou arquivos de imagem difíceis de versionar no Git, utilizamos o conceito de *Diagrams as Code*.

O script abaixo utiliza a biblioteca `graphviz` para desenhar um esquema estrela simples. Note como utilizamos tabelas HTML injetadas nos nós para formatar visualmente as entidades.

```python
import graphviz

# 1. Inicializa o diagrama direcionado (Digraph)
dot = graphviz.Digraph('StarSchema', node_attr={'shape': 'plaintext'})

# 2. Criando a Tabela Fato no centro
# A tag PORT define a âncora visual onde a seta do relacionamento vai conectar
dot.node('FatoVendas', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR><TD BGCOLOR="#ffcccb"><B>Fato_Vendas</B></TD></TR>
  <TR><TD PORT="fk_tempo">id_tempo (FK)</TD></TR>
  <TR><TD PORT="fk_produto">id_produto (FK)</TD></TR>
  <TR><TD>quantidade_vendida</TD></TR>
  <TR><TD>valor_total</TD></TR>
</TABLE>>''')

# 3. Criando uma Tabela Dimensão
dot.node('DimProduto', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR><TD BGCOLOR="#add8e6"><B>Dim_Produto</B></TD></TR>
  <TR><TD PORT="pk_produto">id_produto (PK)</TD></TR>
  <TR><TD>nome_produto</TD></TR>
  <TR><TD>categoria</TD></TR>
  <TR><TD>marca</TD></TR>
</TABLE>>''')

# 4. Criando o relacionamento (Aresta / Edge)
# O formato é 'Origem:porta', 'Destino:porta'
dot.edge('FatoVendas:fk_produto', 'DimProduto:pk_produto', label='1:N')

# 5. Renderiza a imagem e salva como 'modelo_vendas.png'
dot.render('modelo_vendas', format='png')
```

## 5. Glossário

Para facilitar os estudos, aqui está o resumo dos termos técnicos mais importantes da semana:

* **Data Warehouse (DW):** Repositório central de dados estruturados focado em consultas e análises (Analytics).
* **Desnormalização:** Estratégia de modelagem de dados onde regras estritas são afrouxadas para adicionar dados redundantes em uma tabela, visando diminuir a quantidade de `JOINs` e acelerar consultas de leitura.
* **Granularidade:** O nível de detalhe que uma única linha de uma Tabela Fato representa. (ex: Uma linha é a soma das vendas do dia todo? Ou uma linha é um único item passando no caixa?). Quanto mais detalhado, maior a granularidade.
* **Join:** Operação utilizada em bancos de dados relacionais para combinar registros de duas ou mais tabelas baseadas em uma coluna comum entre elas (geralmente PK e FK).
* **Normalização:** O processo de organizar dados em um banco relacional para reduzir redundâncias e garantir a integridade dos dados (evitando anomalias de atualização ou exclusão).
* **Surrogate Key (Chave Substituta):** Uma chave primária artificial, geralmente um número inteiro sequencial gerado pelo banco de dados, muito usada em Tabelas Dimensão em vez de chaves naturais (como CPFs ou códigos de produto legados).
