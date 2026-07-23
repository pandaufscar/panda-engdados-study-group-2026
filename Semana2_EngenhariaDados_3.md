# Semana 2 — Fontes de Dados, APIs e ETL vs ELT

*Minicurso de Engenharia de Dados · Panda 2026*

---

## Teoria

### Fontes de dados: arquivos, APIs e bancos

Exemplos de tipos de arquivos:
* CSV
* Excel (.xlsx)
* JSON
* TXT
* Parquet (muito usado no mercado)

Exemplos de Banco:

Relacionais (SQL):
* PostgreSQL
* MySQL
* SQL Server

Não relacionais (NoSQL):
* MongoDB
* Cassandra

#### Sobre o Parquet

Utilizado com estruturas de Big Data como Spark. Ao contrário dos formatos baseados em linhas, como o CSV, o Parquet organiza os **dados em colunas**. Isso significa que, quando executamos uma consulta, ela extrai apenas as colunas específicas de que precisamos, em vez de carregar tudo. Isso melhora o desempenho e reduz o uso de E/S.

![Diagrama da arquitetura interna do Parquet](images/parquet_arquitetura_interna.png)

**Grupos de linhas**

Um grupo de linhas contém várias linhas, mas armazena os dados em colunas para uma leitura eficiente.
Exemplo: Um conjunto de dados com 1 milhão de linhas pode ser dividido em 10 grupos de 100.000 linhas cada.

**Partes de coluna**

Em cada grupo de linhas, os dados são separados por colunas.
Esse design permite a poda colunar, em que podemos ler apenas as colunas relevantes em vez de examinar o arquivo inteiro.

**Páginas**

Cada bloco de coluna é dividido em páginas para otimizar o uso da memória.
Normalmente, as páginas são compactadas, reduzindo os custos de armazenamento.

**Rodapé (metadados)**

O rodapé no final de um arquivo Parquet armazena informações de índice:
Schema: Define tipos de dados e nomes de colunas.
Offsets de grupos de linhas: Ajuda a localizar dados específicos rapidamente.
Estatísticas: Valores mínimo/máximo para ativar o pushdown do predicado (filtragem no nível de armazenamento).

### API REST


O que é REST?

REST (Representational State Transfer) é um padrão de arquitetura para APIs web.

Na prática:

* usa HTTP
* usa URLs (endpoints): Endereço do recurso
* retorna dados (geralmente JSON)

#### Verbos HTTP (o que você quer fazer com o recurso)

| Verbo | Uso | Exemplo |
|---|---|---|
| `GET` | Buscar dado (o mais usado em pipelines de dados) | `GET /usuarios/123` |
| `POST` | Criar um novo recurso | `POST /usuarios` |
| `PUT` | Atualizar um recurso inteiro | `PUT /usuarios/123` |
| `PATCH` | Atualizar parte de um recurso | `PATCH /usuarios/123` |
| `DELETE` | Remover um recurso | `DELETE /usuarios/123` |

Em engenharia de dados, o dia a dia é dominado por `GET` — você está consumindo dados que já existem, não criando/alterando nada na fonte.

#### Códigos de status HTTP (o que a resposta te diz)

A resposta de toda chamada HTTP vem com um código de status. Reconhecer os principais evita muita dor de cabeça:

* **2xx — sucesso**
  * `200 OK` → deu certo
  * `201 Created` → criou algo com sucesso
* **4xx — erro seu (cliente)**
  * `400 Bad Request` → a requisição está mal formada
  * `401 Unauthorized` / `403 Forbidden` → falta autenticação ou permissão
  * `404 Not Found` → o recurso não existe
  * `429 Too Many Requests` → você estourou o limite de chamadas (rate limit)
* **5xx — erro do servidor**
  * `500 Internal Server Error` → problema do lado da API, não é culpa sua

📌 **Por que isso importa pra engenharia de dados:** todo pipeline que consome API deveria checar `response.status_code` antes de seguir em frente — é exatamente o que o código da seção Prática faz (`if response.status_code != 200: raise Exception(...)`). Sem essa checagem, um erro na API vira um erro confuso de JSON mais na frente do código, longe da causa real.

#### Headers, autenticação e o fato de REST ser stateless

* **Headers** carregam metadados da requisição — os dois mais comuns em engenharia de dados são `Authorization` (autenticação) e `Content-Type` (formato do corpo, geralmente `application/json`).
* **Autenticação**: a maioria das APIs pagas/privadas exige uma **API Key** (uma chave única enviada no header) ou um token **OAuth**. Sem isso, a resposta vem `401`/`403`.
* **REST é stateless**: cada requisição é independente — o servidor não guarda memória da chamada anterior. Isso significa que toda informação necessária (autenticação, filtros, paginação) precisa ir em *cada* requisição.

### Biblioteca requests (Python)

Permite:

* consumir APIs
* integrar sistemas
* automatizar coleta de dados


```
requests.get(url)


response.json()
```


#### Indo além do básico: parâmetros, headers e timeout

O exemplo mínimo é `requests.get(url)`, mas no dia a dia você quase sempre precisa de mais controle:

```python
resposta = requests.get(
    url,
    headers={"Authorization": "Bearer SEU_TOKEN"},   # autenticação
    params={"page": 1, "limit": 100},                 # query string (?page=1&limit=100)
    timeout=10                                          # não trava esperando pra sempre
)
```

* `headers` → autenticação e formato esperado
* `params` → o `requests` monta a query string pra você (evita concatenar string manualmente)
* `timeout` → sem isso, um servidor lento pode travar seu pipeline indefinidamente

#### O erro nº 1 de quem está começando com APIs

Chamar `.json()` direto numa resposta que veio com erro (404, 500...) quebra com um `JSONDecodeError` que **parece não ter nada a ver** com a causa real — porque o corpo da resposta de erro geralmente não é um JSON válido no formato esperado.

```python
# ❌ Perigoso: não checa status antes de decodificar
dados = requests.get(url).json()

# ✅ Seguro: falha com uma mensagem que aponta a causa real
resposta = requests.get(url)
if resposta.status_code != 200:
    raise Exception(f"Erro ao acessar API: {resposta.status_code}")
dados = resposta.json()
```

Isso é exatamente o padrão usado na seção **Prática** deste notebook — guarde esse hábito, é o erro mais comum de quem está começando com APIs.

#### JSON aninhado: quando `pd.DataFrame()` não é suficiente

`pd.DataFrame(dados)` funciona bem quando o JSON já é uma lista de objetos "planos" — como é o caso da API PTAX usada neste notebook (`data["value"]`). Mas é muito comum encontrar JSON **aninhado** por aí, tipo:

```json
{
  "usuario": {
    "nome": "Ana",
    "endereco": {"cidade": "SP", "cep": "01000-000"}
  }
}
```

Nesses casos, a ferramenta certa é `pd.json_normalize()`, que "achata" a estrutura em colunas (`usuario.nome`, `usuario.endereco.cidade`, ...). Exemplo ilustrativo (não usa os dados da PTAX):


```python
import pandas as pd

dados_aninhados = [
    {"usuario": {"nome": "Ana", "endereco": {"cidade": "SP"}}},
    {"usuario": {"nome": "Beto", "endereco": {"cidade": "RJ"}}},
]

df_normalizado = pd.json_normalize(dados_aninhados)
df_normalizado
```

Vale sempre inspecionar `dados.keys()` (ou o primeiro item de uma lista) antes de decidir entre `pd.DataFrame()` direto ou `pd.json_normalize()` — foi exatamente essa inspeção que ajudou a descobrir que os dados da PTAX estavam dentro de `"value"` neste notebook.

### Conceitos de ETL (Extract, Transform, Load) e ELT

1. Extract

Buscar dados da fonte (API, arquivo, banco)

2. Transform

Limpar, organizar, padronizar

3. Load

Salvar em destino final

📌 Exemplo prático
API → extrair dados
pandas → limpar
CSV → salvar

**ELT**

API → salva bruto no banco
SQL → transforma depois


🎯 Visão de mercado

Hoje, ELT é MUITO usado em:

Data Warehouses
BigQuery
Snowflake
Redshift

👉 Especialmente com ferramentas como dbt

### Onde os dados moram: Data Lake vs Data Warehouse vs Lakehouse

ETL e ELT descrevem **quando** a transformação acontece. Mas fica uma pergunta: **onde** os dados ficam guardados nesse processo? É aqui que entram três termos que aparecem o tempo todo no mercado.

**Data lake** — armazenamento barato e flexível (ex: Amazon S3, Google Cloud Storage) que guarda o dado **bruto**, exatamente como chegou: CSV, JSON, imagem, log, o que for. Não exige estrutura (*schema-on-read*: a estrutura só é aplicada quando alguém lê, não quando o dado é gravado). Ótimo pra custo e flexibilidade, mas sozinho não serve pra análise direta.

**Data warehouse** — armazenamento estruturado, mais caro, feito pra consulta SQL rápida. Os dados chegam em tabelas com schema definido, prontos pra ferramenta de BI consumir.

No modelo clássico, são **dois sistemas separados**, e o ETL é a ponte entre eles: extrai do lake, limpa/organiza, e só então carrega no warehouse.

**Data lakehouse** — a resposta moderna ao problema de manter dois sistemas separados (custa caro, gera atraso, e o lake sem governança vira um "pântano de dados"). O lakehouse (Databricks com Delta Lake, ou tabelas Iceberg) junta os dois num sistema só: armazenamento barato do lake, com recursos de warehouse por cima (transações ACID, schema, SQL). Em vez de mover o dado pra outro sistema pra organizá-lo, você organiza *no mesmo lugar*, em camadas — é aqui que entra a arquitetura medallion.

#### Arquitetura medallion — bronze, silver, gold

A forma mais comum de organizar as camadas dentro de um lakehouse (ou de qualquer ELT moderno):

| Camada | O que é | Equivalente neste notebook |
|---|---|---|
| 🥉 **Bronze** | Dado exatamente como chegou da fonte, sem tratamento | O `ptax_raw.json` salvo antes de qualquer limpeza |
| 🥈 **Silver** | Dado limpo — nulos tratados, tipos convertidos, colunas padronizadas | O `df` depois do `pd.to_datetime(...)` |
| 🥇 **Gold** | Dado agregado, modelado pra consumo — métricas prontas, dashboard, relatório | Não chegamos a essa etapa aqui; seria, por exemplo, uma tabela de cotação média por mês |

Cada camada é uma tabela/arquivo separado — você nunca sobrescreve o bruto, só empilha transformações por cima. Isso é o que permite reprocessar do zero se encontrar um bug na limpeza, sem depender da API de novo.

**Nota importante:** ETL/ELT (quando transforma) e lake/warehouse/lakehouse (onde o dado mora) são eixos relacionados, mas **independentes**. Dá pra fazer ETL carregando num lakehouse, e é comum fazer ELT carregando num warehouse moderno (é literalmente o que Snowflake e BigQuery foram desenhados pra fazer bem, geralmente combinados com dbt).

### Postman

O que é?

Ferramenta para testar APIs sem código.

📌 Para que serve?

* testar endpoints
* ver JSON
* validar parâmetros
* entender resposta

### Pontos para se atentar

#### 1) PAGINAÇÃO — “o dado não vem todo de uma vez”

**Problema real**

Quando você chama uma API, ela quase nunca te entrega todos os dados de uma vez.

**Por quê?**

Porque:

* pode ser muito volume
* pode sobrecarregar o servidor
* pode travar sua aplicação
* pode violar limites de uso

Então a API responde algo como:

“Aqui vão os primeiros 100 registros. Se quiser mais, peça a próxima página.

Como aparece na prática:
Você faz uma requisição e recebe:

```
{
  "data": [...],
  "page": 1,
  "total_pages": 10
}

```


Ou:


```
{
  "results": [...],
  "next": "https://api.com?page=2"
}
```


**Estratégias de paginação**

1. Por número de página:

?page=1
?page=2

2. Por offset:

?offset=0&limit=100

3. Cursor-based (mais avançado):

?cursor=abc123

4. Por data:

?created_after=2025-01-01

#### 2) RATE LIMIT — “você não pode sair pedindo tudo”

**Técnicas usadas no mercado**

1. Throttling (controle de ritmo):

import time
time.sleep(1)

2. Retry com backoff

Se der erro:

espera
tenta de novo
aumenta o tempo de espera

3. Cache

Se já buscou:

não busca de novo

4. Filtragem inteligente

Em vez de pegar tudo:

?date=today

5. Batch requests (quando possível)

Pedir vários dados em uma requisição só.

#### 3) AUTENTICAÇÃO — “nem todo mundo pode acessar tudo”

**Problemas reais de segurança:**

1. Expor chave no código

API_KEY = "abc123"

 Se subir no GitHub:

* chave vazada
* qualquer pessoa pode usar
* custo para você
* risco de bloqueio

2. Não usar HTTPS

Pode expor dados na rede.

3. Não rotacionar chave

Chaves devem ser trocadas periodicamente.

Para resolver:

1.**Variáveis de ambiente**

Em vez de colocar no código:

import os
API_KEY = os.getenv("API_KEY")


2.**Arquivo .env**

API_KEY=abc123

E nunca subir isso no GitHub (.gitignore)

3.**Controle de acesso**

limitar permissões
usar tokens com escopo

4.**Monitoramento**

quem está usando?
quantas requisições?
comportamento estranho?

### Checklist de boas práticas

**✅ Faça**
* Sempre cheque `status_code` antes de usar `.json()`
* Valide/converta tipos de dados antes de salvar (`pd.to_datetime`, `astype`)
* Salve o dado bruto separado do tratado (é a base da arquitetura medallion)
* Use nomes de coluna padronizados (`df.columns = df.columns.str.lower()`)
* Guarde credenciais em variável de ambiente / `.env`, nunca no código

**❌ Evite**
* Ignorar erros da API (404, 429, 500) — trate-os explicitamente
* Misturar dado bruto com dado já tratado no mesmo arquivo/pasta
* Fixar caminhos de arquivo "hardcoded" quando outras pessoas vão rodar o notebook
* Repetir chamadas à API sem necessidade (rate limit pode bloquear seu acesso)
* Subir chave de API pro GitHub

## Prática

### Extract


```python
import requests
import pandas as pd

url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='01-01-2020'&@dataFinalCotacao='04-01-2026'&$top=10000&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao"


response = requests.get(url)

print("Status Code:", response.status_code)
```

    Status Code: 200


```python
if response.status_code != 200:
    raise Exception(f"Erro ao acessar API: {response.status_code}")
```


```python
data = response.json()

data
```


    {'@odata.context': 'https://was-p.bcnet.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata$metadata#_CotacaoDolarPeriodo(cotacaoCompra,cotacaoVenda,dataHoraCotacao)',
     'value': [{'cotacaoCompra': 4.0207,
       'cotacaoVenda': 4.0213,
       'dataHoraCotacao': '2020-01-02 13:11:10.762'},
      {'cotacaoCompra': 4.0516,
       'cotacaoVenda': 4.0522,
       'dataHoraCotacao': '2020-01-03 13:06:22.606'},
      ...
      # saída truncada neste markdown (1.570 registros no total) — ver notebook original para o JSON completo
     ]}


Transformar Json em Df

**Atenção:** usando :

```
data.keys()
```
Dá para ver que os dados estão na verdade em "values".


#### Baixando arquivo "RAW"


```python
import json
with open("ptax_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON bruto salvo")
```

    JSON bruto salvo


Uso de "encoding ="utf-8" para evitar erros de leitura de caracteres especiais.


### Load


```python
import pandas as pd

df = pd.DataFrame(data["value"])

df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 1570 entries, 0 to 1569
    Data columns (total 3 columns):
     #   Column           Non-Null Count  Dtype  
    ---  ------           --------------  -----  
     0   cotacaoCompra    1570 non-null   float64
     1   cotacaoVenda     1570 non-null   float64
     2   dataHoraCotacao  1570 non-null   object 
    dtypes: float64(2), object(1)
    memory usage: 36.9+ KB


Como já vem no formato certo a "cotacaoVenda" e a "cotacaoCompra", logo só é necessário mudar "dataHoraCotacao" para datetime.


```python
df["dataHoraCotacao"] = pd.to_datetime(df["dataHoraCotacao"])

df
```

|   | cotacaoCompra | cotacaoVenda | dataHoraCotacao |
|---|---|---|---|
| 0 | 4.0207 | 4.0213 | 2020-01-02 13:11:10.762 |
| 1 | 4.0516 | 4.0522 | 2020-01-03 13:06:22.606 |
| 2 | 4.0548 | 4.0554 | 2020-01-06 13:03:22.271 |
| 3 | 4.0835 | 4.0841 | 2020-01-07 13:06:14.601 |
| 4 | 4.0666 | 4.0672 | 2020-01-08 13:03:56.075 |
| ... | ... | ... | ... |
| 1565 | 5.2302 | 5.2308 | 2026-03-26 13:11:08.561 |
| 1566 | 5.2370 | 5.2376 | 2026-03-27 13:11:42.090 |
| 1567 | 5.2347 | 5.2353 | 2026-03-30 13:10:27.787 |
| 1568 | 5.2188 | 5.2194 | 2026-03-31 13:04:22.650 |
| 1569 | 5.1600 | 5.1606 | 2026-04-01 13:06:27.728 |
<p>1570 rows × 3 columns</p>

```python
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 1570 entries, 0 to 1569
    Data columns (total 3 columns):
     #   Column           Non-Null Count  Dtype         
    ---  ------           --------------  -----         
     0   cotacaoCompra    1570 non-null   float64       
     1   cotacaoVenda     1570 non-null   float64       
     2   dataHoraCotacao  1570 non-null   datetime64[ns]
    dtypes: datetime64[ns](1), float64(2)
    memory usage: 36.9 KB


#### 🎁 Indo além: padronizando nomes de coluna (opcional)

Boa prática de mercado antes de salvar: colunas com nomes padronizados evitam bugs silenciosos depois (ex: alguém escrever `DataHoraCotacao` em vez de `dataHoraCotacao`).


```python
df.columns = df.columns.str.lower()

df.columns
```

### Load


```python
df.to_csv("ptax_tratado.csv", index=False)

print("CSV tratado salvo")

from google.colab import files
files.download("ptax_tratado.csv")

```

    CSV tratado salvo


### Explorar dados


```python
df.describe()
```

|   | cotacaoCompra | cotacaoVenda | dataHoraCotacao |
|---|---|---|---|
| count | 1570.000000 | 1570.000000 | 1570 |
| mean | 5.281332 | 5.281939 | 2023-02-17 12:20:13.226776832 |
| min | 4.020700 | 4.021300 | 2020-01-02 13:11:10.762000 |
| 25% | 5.067625 | 5.068225 | 2021-07-27 19:09:27.265500160 |
| 50% | 5.284100 | 5.284700 | 2023-02-15 01:07:18.724499968 |
| 75% | 5.509000 | 5.509600 | 2024-09-10 07:09:16.800000 |
| max | 6.208000 | 6.208600 | 2026-04-01 13:06:27.728000 |
| std | 0.344296 | 0.344300 | NaN |


```python
import matplotlib.pyplot as plt

plt.plot(df["dataHoraCotacao"], df["cotacaoVenda"])
plt.show()

```

![Gráfico da cotação do dólar (PTAX) ao longo do tempo](images/grafico_cotacao_dolar_ptax.png)

```python
df[df["cotacaoVenda"] > 5.0].head()

```

|   | cotacaoCompra | cotacaoVenda | dataHoraCotacao |
|---|---|---|---|
| 51 | 5.0489 | 5.0496 | 2020-03-17 13:05:19.726 |
| 52 | 5.1101 | 5.1107 | 2020-03-18 13:06:00.426 |
| 53 | 5.1437 | 5.1444 | 2020-03-19 13:08:32.134 |
| 54 | 5.0241 | 5.0248 | 2020-03-20 13:03:05.621 |
| 55 | 5.0798 | 5.0805 | 2020-03-23 13:03:28.802 |


### Conclusão

Foi desenvolvido um pipeline de dados consumindo a API PTAX do Banco Central.

#### Etapas realizadas:
- Consumo de API REST com requests
- Validação da resposta HTTP
- Salvamento dos dados brutos em JSON
- Transformação para DataFrame
- Conversão de tipos e padronização de colunas
- Salvamento dos dados tratados em CSV

#### Principais desafios:
- Uso correto do endpoint da API PTAX
- Tratamento da estrutura JSON (campo "value")
- Conversão de datas e tipos numéricos

O dataset final está pronto para análises financeiras e séries temporais.

### 📚 Glossário rápido

| Termo | Definição curta |
|---|---|
| **API** | Interface para dois sistemas conversarem (*Application Programming Interface*) |
| **REST** | Estilo de arquitetura de API sobre HTTP (recursos, verbos, status codes) |
| **JSON** | Formato de dados chave-valor, quase universal em APIs |
| **Endpoint** | URL que representa um recurso específico da API |
| **Rate limit** | Limite de chamadas por período que uma API permite |
| **Paginação** | Técnica pra API devolver resultados grandes em partes |
| **ETL** | Extract → **T**ransform → Load — transforma antes de carregar |
| **ELT** | Extract → Load → **T**ransform — carrega bruto, transforma depois |
| **Data lake** | Armazenamento barato de dado bruto, schema-on-read |
| **Data warehouse** | Armazenamento estruturado, caro, pronto pra SQL/BI |
| **Data lakehouse** | Lake + warehouse num sistema só (ex: Databricks/Delta Lake) |
| **Medallion (bronze/silver/gold)** | Camadas de organização dentro de um lakehouse |
| **Parquet** | Formato colunar, comprimido, eficiente pra Big Data/Spark |
| **Schema-on-read vs schema-on-write** | Estrutura aplicada na leitura (lake) vs na escrita (warehouse) |
| **dbt** | Ferramenta que roda transformações em SQL dentro do warehouse (o "T" do ELT) |

### 🎯 Perguntas de entrevista — Engenharia de Dados Jr

Perguntas que costumam aparecer em entrevistas de estágio/júnior sobre o conteúdo deste notebook, com respostas curtas de referência. Tente responder mentalmente antes de ler a resposta.

**1. Qual a diferença entre ETL e ELT?**
ETL transforma antes de carregar (o Transform acontece entre o Extract e o Load); ELT carrega o dado bruto primeiro e transforma depois, dentro do próprio destino. A diferença é a *ordem* das operações, não a tecnologia usada.

**2. Data warehouse é sempre ETL e data lake é sempre ELT?**
Não — essa é uma simplificação comum, mas incorreta. ETL/ELT descreve a ordem das operações; lake/warehouse descreve *onde* o dado mora. Dá pra fazer ETL carregando num lakehouse, e é super comum fazer ELT carregando num warehouse moderno — Snowflake e BigQuery são literalmente desenhados pra isso.

**3. O que é a arquitetura medallion?**
Um jeito de organizar dados dentro de um lakehouse em camadas progressivas: bronze (bruto), silver (limpo/validado), gold (agregado, pronto pro negócio).

**4. Por que guardar o dado bruto (bronze) se ele vai ser tratado de qualquer jeito?**
Permite reprocessar do zero se um bug for encontrado na limpeza, sem depender de bater na fonte de novo — economiza tempo e preserva o histórico original.

**5. O que é uma API REST?**
Uma interface que expõe recursos via HTTP, usando verbos (GET/POST/PUT/DELETE) e retornando dados — geralmente em JSON — seguindo princípios como statelessness.

**6. Qual verbo HTTP você usa pra buscar dados numa API?**
`GET`.

**7. O que significa um status 429? E um 401?**
`429` = você estourou o rate limit (limite de chamadas). `401` = falta autenticação, ou ela está incorreta.

**8. Por que sempre checar `status_code` antes de chamar `.json()`?**
Porque uma resposta de erro (404, 500...) geralmente não tem um corpo JSON válido no formato esperado — chamar `.json()` direto gera um erro confuso (`JSONDecodeError`) que esconde a causa real do problema.

**9. Como lidar com uma API que pagina os resultados?**
Ler o campo de paginação da resposta (ex: `total_pages`, ou um link `next`) e fazer requisições sucessivas até não haver mais páginas, acumulando os resultados.

**10. Como lidar com rate limit na prática?**
Técnicas comuns: throttling (`time.sleep()` entre chamadas), retry com backoff exponencial, cache de respostas já buscadas, e filtrar/pedir só o necessário em vez de tudo de uma vez.

**11. Onde guardar uma API key com segurança?**
Em variável de ambiente (`os.getenv()`) ou arquivo `.env` (fora do controle de versão via `.gitignore`) — nunca direto no código-fonte.

**12. Qual a vantagem do Parquet sobre o CSV?**
Parquet é colunar (uma consulta lê só as colunas necessárias, não a linha inteira) e comprimido — reduz I/O e melhora performance em consultas analíticas, especialmente em ambientes de Big Data/Spark.

**13. Quando usar `pd.json_normalize()` em vez de `pd.DataFrame()` direto?**
Quando o JSON de resposta é aninhado (objetos dentro de objetos) — `json_normalize` achata a estrutura em colunas.

**14. Dê um exemplo de pipeline ETL simples.**
Extrair de uma API pública → limpar com pandas (tipos, nulos, nomes de coluna) → salvar em CSV. É exatamente o pipeline construído neste notebook.
