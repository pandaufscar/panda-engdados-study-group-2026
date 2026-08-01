# Semana 5 — ETL/ELT avançado, qualidade e logs

Nesta semana, o objetivo é evoluir de um script linear para um **pipeline de dados modular, confiável e observável**. Além de extrair, transformar e carregar dados, o pipeline deve verificar sua qualidade, registrar cada etapa da execução e responder de forma controlada a falhas comuns.

## Objetivos de aprendizagem

Ao final da semana, espera-se que você consiga:

- diferenciar ETL de ELT;
- dividir um pipeline em funções com responsabilidades específicas;
- verificar nulos, duplicados, tipos e inconsistências;
- usar logs para acompanhar a execução;
- tratar erros com `try` e `except`;
- simular falhas para testar o comportamento do pipeline.

---

## 1. ETL e ELT

ETL e ELT são estratégias usadas para mover e preparar dados.

| Estratégia | Ordem | Característica principal |
|---|---|---|
| **ETL** | Extract → Transform → Load | Os dados são transformados antes de chegar ao destino. |
| **ELT** | Extract → Load → Transform | Os dados brutos são carregados primeiro e transformados no ambiente de destino. |

### ETL — Extract, Transform, Load

1. **Extração:** coleta os dados de arquivos, APIs, bancos de dados ou outras fontes.
2. **Transformação:** limpa, valida e padroniza os dados.
3. **Carga:** salva os dados tratados no destino escolhido.

O notebook desta semana utiliza ETL: os dados são extraídos, tratados e somente depois salvos em `coletas_tratadas.csv`.

### Quando o ELT é útil?

O ELT é comum quando o destino, como um data lake ou data warehouse em nuvem, possui capacidade para armazenar os dados brutos e executar as transformações. Isso preserva a fonte original e permite diferentes tratamentos posteriores.

---

## 2. Modularização de pipelines

Modularizar significa dividir o pipeline em partes menores, cada uma responsável por uma tarefa. Em vez de colocar todas as instruções em um único bloco, criamos funções independentes.

```text
Extração → Validação de estrutura → Validação de qualidade
         → Transformação → Carga
```

No pipeline da prática, as responsabilidades foram separadas assim:

| Função | Responsabilidade |
|---|---|
| `extrair_dados()` | Obter ou criar os dados brutos. |
| `validar_estrutura()` | Conferir a presença das colunas obrigatórias. |
| `validar_qualidade()` | Identificar nulos, duplicados e valores inválidos. |
| `transformar_dados()` | Limpar, converter e padronizar os registros. |
| `carregar_dados()` | Salvar os dados tratados. |
| `executar_pipeline()` | Coordenar todas as etapas e tratar falhas. |

### Vantagens da modularização

- facilita a leitura e a manutenção do código;
- permite testar cada etapa isoladamente;
- reduz repetição;
- torna as funções reutilizáveis;
- ajuda a localizar erros;
- permite alterar uma etapa sem reescrever todo o pipeline.

Exemplo de função com uma única responsabilidade:

```python
def carregar_dados(df, caminho_saida="coletas_tratadas.csv"):
    df.to_csv(caminho_saida, index=False)
    return caminho_saida
```

---

## 3. Qualidade de dados

Dados de baixa qualidade podem produzir análises incorretas, mesmo quando o código funciona. Por isso, a qualidade precisa ser verificada antes que a informação seja utilizada.

### 3.1 Valores nulos

Um valor nulo representa uma informação ausente. Dependendo da coluna e do objetivo da análise, ele pode ser preenchido, mantido ou causar a remoção do registro.

```python
df.isnull().sum()
```

No exemplo, `pesquisador` é uma coluna crítica. Uma linha sem essa informação é removida durante a transformação.

### 3.2 Linhas duplicadas

Duplicados podem causar contagens incorretas e distorcer resultados.

```python
total_duplicados = df.duplicated().sum()
df = df.drop_duplicates()
```

O método `duplicated()` identifica as cópias e `drop_duplicates()` mantém apenas um dos registros repetidos.

### 3.3 Tipos inválidos

Uma coluna numérica pode receber um texto por erro de digitação ou de integração. O pandas permite tentar a conversão e transformar valores incompatíveis em nulos:

```python
df["volume_ml"] = pd.to_numeric(df["volume_ml"], errors="coerce")
```

Com `errors="coerce"`, um valor como `"quinhentos"` torna-se `NaN`. Depois, o pipeline pode decidir como tratá-lo.

### 3.4 Consistência

Mesmo com o tipo correto, um valor pode ser incompatível com as regras do domínio. Por exemplo, um volume igual ou menor que zero é numérico, mas não é válido para uma amostra.

```python
df = df[df["volume_ml"] > 0]
```

Outros exemplos de consistência incluem datas impossíveis, identificadores fora do padrão e categorias escritas de formas diferentes.

### Validar não é o mesmo que transformar

- **Validação:** detecta e informa os problemas.
- **Transformação:** corrige, padroniza ou remove os registros problemáticos.

Separar essas responsabilidades deixa explícito o que foi encontrado e qual decisão foi tomada.

---

## 4. Transformação dos dados

Na prática, a função `transformar_dados()`:

1. cria uma cópia dos dados brutos;
2. remove duplicados;
3. converte volume e data para os tipos esperados;
4. remove espaços extras dos textos;
5. elimina registros com dados críticos ausentes ou inválidos;
6. mantém apenas volumes maiores que zero;
7. cria as colunas `ano`, `mes` e `quantidade_amostras`.

Criar uma cópia evita modificar diretamente o conjunto original:

```python
df_tratado = df.copy()
```

A padronização de textos pode ser feita com:

```python
df_tratado["pesquisador"] = (
    df_tratado["pesquisador"]
    .astype("string")
    .str.strip()
)
```

---

## 5. Logging em pipelines

Logs são registros automáticos dos eventos ocorridos durante a execução. Eles ajudam a descobrir:

- qual etapa está sendo executada;
- quantos registros foram processados;
- quais problemas foram encontrados;
- se o pipeline terminou com sucesso;
- em qual ponto ocorreu uma falha.

### Configuração básica

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)
```

O formato contém horário, nível e mensagem. Exemplo:

```text
2026-04-01 10:00:00 - INFO - Iniciando extração dos dados.
```

### Principais níveis de log

| Nível | Uso |
|---|---|
| `DEBUG` | Detalhes úteis durante o desenvolvimento. |
| `INFO` | Eventos normais, como início e conclusão de uma etapa. |
| `WARNING` | Situação inesperada que não impede necessariamente o fluxo. |
| `ERROR` | Falha que impede uma operação ou etapa. |
| `CRITICAL` | Problema grave que compromete todo o sistema. |

Exemplos usados no notebook:

```python
logging.info("Iniciando transformação dos dados.")
logging.warning("Foram encontradas %s linhas duplicadas.", total)
logging.error("Erro de validação: %s", erro)
```

Usar parâmetros como `%s` é preferível a montar a mensagem antecipadamente, pois o próprio módulo de logging faz a formatação quando necessário.

---

## 6. Tratamento de erros

O bloco `try/except` permite executar uma operação e definir como o programa deve reagir caso ocorra uma exceção.

```python
try:
    dados_brutos = extrair_dados()
    validar_estrutura(dados_brutos)
    dados_tratados = transformar_dados(dados_brutos)
except ValueError as erro:
    logging.error("Erro de validação: %s", erro)
except Exception as erro:
    logging.error("Erro inesperado: %s", erro)
```

Capturar primeiro uma exceção específica, como `ValueError`, permite gerar uma resposta clara. O `Exception` mais geral fica por último para falhas não previstas.

### Falhar cedo

Se uma coluna obrigatória estiver ausente, é melhor interromper o pipeline na validação de estrutura do que continuar até uma transformação falhar com uma mensagem difícil de interpretar.

```python
if colunas_ausentes:
    raise ValueError(
        f"Colunas obrigatórias ausentes: {colunas_ausentes}"
    )
```

---

## 7. Simulação de falhas

Testar apenas o cenário ideal não demonstra que um pipeline é confiável. A prática utiliza o parâmetro `simular_erro` para provocar dois problemas.

### Cenário 1 — campo ausente

```python
executar_pipeline(simular_erro="campo_ausente")
```

A extração remove `volume_ml`. Como essa coluna é obrigatória, `validar_estrutura()` gera um `ValueError`, o erro é registrado e a execução é interrompida de forma controlada.

### Cenário 2 — tipo inválido

```python
executar_pipeline(simular_erro="tipo_invalido")
```

O valor `"quinhentos"` é inserido em `volume_ml`. A validação gera um aviso; na transformação, o texto é convertido em `NaN` e a linha é removida. Nesse caso, o pipeline consegue continuar.

| Falha simulada | Classificação | Comportamento |
|---|---|---|
| Coluna `volume_ml` ausente | Erro estrutural | Interrompe o pipeline. |
| Texto em `volume_ml` | Problema de qualidade | É registrado e tratado. |

Essa diferença é importante: nem todo problema precisa interromper o fluxo, mas toda decisão deve ser conhecida e registrada.

---

## 8. Resultado da execução normal

A base inicial contém cinco linhas. Durante o tratamento:

- uma linha duplicada é removida;
- uma linha sem pesquisador é removida por falta de dado crítico;
- três linhas válidas permanecem.

```text
5 linhas brutas − 1 duplicada − 1 com dado crítico nulo = 3 linhas tratadas
```

O resultado é salvo em `coletas_tratadas.csv`. A redução não ocorre aleatoriamente: cada exclusão segue uma regra explícita de qualidade.

---

## 9. Visão geral do pipeline

```python
def executar_pipeline(simular_erro=None):
    try:
        dados_brutos = extrair_dados(simular_erro)
        validar_estrutura(dados_brutos)
        validar_qualidade(dados_brutos)
        dados_tratados = transformar_dados(dados_brutos)
        caminho = carregar_dados(dados_tratados)
        return dados_tratados, caminho
    except ValueError as erro:
        logging.error("Erro de validação: %s", erro)
        return None, None
    except Exception as erro:
        logging.error("Erro inesperado: %s", erro)
        return None, None
```

Essa função atua como orquestradora: chama as etapas na ordem correta e centraliza o tratamento das exceções.

---

## 10. Governança e segurança de dados

Além da qualidade técnica, pipelines reais precisam considerar governança e privacidade.

- **Controle de acesso:** somente pessoas autorizadas devem acessar dados sensíveis.
- **Privilégio mínimo:** cada usuário deve receber apenas as permissões necessárias.
- **Rastreabilidade:** alterações e acessos importantes devem ser registrados.
- **Minimização:** devem ser coletados somente os dados necessários.
- **Proteção:** informações sensíveis podem exigir criptografia, anonimização ou pseudonimização.
- **Retenção:** dados não devem ser armazenados indefinidamente sem justificativa.

Logs também exigem cuidado: senhas, tokens e dados pessoais não devem ser registrados nas mensagens.

---

## Boas práticas resumidas

- mantenha cada função com uma responsabilidade clara;
- valide estrutura e qualidade antes da carga;
- preserve os dados brutos quando possível;
- estabeleça regras de negócio explícitas;
- registre início, fim, contagens, avisos e falhas;
- trate exceções específicas antes das genéricas;
- não silencie erros sem registrar o motivo;
- teste tanto o fluxo normal quanto os cenários de falha;
- evite incluir informações sensíveis nos logs.

---

## Conclusão

Um pipeline confiável não apenas transporta dados. Ele também verifica se a estrutura está correta, identifica problemas de qualidade, aplica regras de transformação, registra o que aconteceu e reage de maneira previsível a erros.

A modularização torna o código mais simples de testar e manter. As validações impedem que dados inadequados avancem silenciosamente. Os logs oferecem visibilidade da execução, e o tratamento de exceções evita falhas confusas ou não controladas.

---

## Glossário

| Termo | Definição |
|---|---|
| **Pipeline** | Sequência automatizada de etapas de processamento de dados. |
| **ETL** | Extração, transformação e carga. |
| **ELT** | Extração, carga e transformação. |
| **Dado bruto** | Dado no formato em que foi recebido, antes do tratamento. |
| **Dado tratado** | Dado validado, limpo e padronizado. |
| **Validação** | Verificação de regras de estrutura ou qualidade. |
| **Logging** | Registro de eventos ocorridos durante a execução. |
| **Exceção** | Evento que interrompe o fluxo normal de um programa. |
| **Consistência** | Compatibilidade do dado com formatos e regras do domínio. |
| **Governança de dados** | Políticas e responsabilidades para uso, proteção e gestão dos dados. |

---

## Materiais complementares

- [Building an End-to-End ETL Pipeline with Python](https://mentorcruise.com/blog/building-an-end-to-end-etl-pipeline-with-python-a-hands-on-guide/)
- [Building a Basic ETL Pipeline in Python with OOP](https://www.tiagovalverde.com/posts/building-a-basic-etl-pipeline-in-python-with-oop)
- [7 Essential Data Quality Checks with pandas](https://www.kdnuggets.com/7-essential-data-quality-checks-with-pandas)
- [Logging HOWTO — documentação do Python](https://docs.python.org/3/howto/logging.html)
- [Debugging Python Data Pipelines](https://dev.to/wachuka_james/debugging-python-data-pipelines-a-step-by-step-guide-11g7)
- [Python Exceptions: An Introduction](https://realpython.com/python-exceptions/)
- [Basics of Data Governance](https://www.ewsolutions.com/basics-of-data-governance/)

## Entrega da semana

Notebook com pipeline modular, separação entre extração, transformação e carga, validações de qualidade, logs de execução, tratamento de erros e simulação de falhas.
