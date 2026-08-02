# Semana 3 - Bancos de Dados Relacionais e SQL

*Minicurso de Engenharia de Dados · PANDA 2026*

*Responsável: Julia Tavares dos Santos*

## Introdução

Nas semanas anteriores os dados foram lidos de arquivos e consumidos de APIs. Esses formatos funcionam bem para trocas pontuais, mas não resolvem o problema de guardar informação de forma organizada, consistente e consultável ao longo do tempo. É para isso que existem os bancos de dados.

Nesta semana o tema é o modelo relacional, que organiza a informação em tabelas conectadas entre si, e o SQL, a linguagem usada para criar essas tabelas, inserir registros e fazer consultas. Também é tratada a normalização, que é o conjunto de regras para evitar dados repetidos, e a conexão entre Python e PostgreSQL, que é o ponto onde o banco entra de fato em um pipeline de dados.

O banco escolhido foi o PostgreSQL, por ser gratuito, amplamente adotado no mercado e possível de instalar dentro da própria sessão do Google Colab, o que dispensa qualquer configuração na máquina de quem está estudando.

## Objetivos de aprendizagem

Ao final desta semana, espera-se ser capaz de:

- explicar o que caracteriza um banco de dados relacional;
- identificar chave primária, chave estrangeira e o tipo de relacionamento entre duas tabelas;
- escrever consultas com `SELECT`, `WHERE`, `ORDER BY`, `JOIN`, `GROUP BY` e `HAVING`;
- reconhecer se um modelo de dados está normalizado e apontar quais problemas a normalização evita;
- conectar Python ao PostgreSQL usando `psycopg2` e `SQLAlchemy`, escrevendo e lendo dados;
- descrever, em linhas gerais, como um banco NoSQL orientado a documentos se diferencia do modelo relacional.

## O que esperar desta entrega

Esta semana é composta por três materiais, que se complementam:

| Material | Formato | Para que serve |
| :--- | :--- | :--- |
| **Slides** | `Semana3_Slides_JuliaTavares.pptx` | Apresentação teórica com 12 slides, incluindo três slides dedicados a leitura de código SQL comentado linha a linha. |
| **Roteiro prático** | `Semana3_Roteiro_JuliaTavares.ipynb` | Notebook do Google Colab que constrói um banco do zero: instalação, criação de tabelas, carga de dados e consultas. É o material que deve ser executado. |
| **Vídeo** | `Semana3_Apresentacao_JuliaTavares_editado.mp4` | Gravação de aproximadamente 15 minutos percorrendo os slides. |

A ordem sugerida é assistir ao vídeo acompanhando os slides e, em seguida, abrir o notebook e executar as células em ordem. Todo o conteúdo teórico apresentado nos slides reaparece aplicado no notebook, sobre o mesmo exemplo.

### Estrutura dos slides

Os slides seguem a identidade visual do minicurso e foram organizados assim:

| Slide | Bloco | Conteúdo |
| :--- | :--- | :--- |
| 1 | Capa | Abertura da semana |
| 2 | Banco relacional | Tabelas, papel do SQL e transações ACID |
| 3 | Chaves e relacionamentos | Chave primária, chave estrangeira e diagrama 1:N |
| 4 | Código | `SELECT`, `WHERE`, `ORDER BY` e `LIMIT` |
| 5 | Código | `JOIN` e `LEFT JOIN` |
| 6 | Código | `GROUP BY` e `HAVING` |
| 7 | Normalização | 1FN, 2FN, 3FN e anomalias evitadas |
| 8 | Comparação | `psycopg2` e `SQLAlchemy` lado a lado |
| 9 | Demonstração guiada | Pipeline Python para PostgreSQL |
| 10 | Opcional | PostgreSQL comparado ao MongoDB |
| 11 | Checklist | O que fazer e o que evitar |
| 12 | Exercício prático | Entrega esperada da semana |

## 1. Bancos de Dados Relacionais

Um banco de dados relacional organiza a informação em **tabelas**. Cada tabela representa uma entidade do mundo real, como um cliente, um produto ou um livro.

Dentro de uma tabela:

- cada **linha** é um registro, ou seja, uma ocorrência daquela entidade;
- cada **coluna** é um atributo, ou seja, uma característica daquela entidade.

A comparação com uma planilha ajuda, mas existe uma diferença importante: em um banco relacional cada coluna tem um tipo de dado definido (texto, número, data), o banco recusa valores fora desse tipo, e as tabelas se conectam umas às outras. É essa conexão que dá nome ao modelo.

| Conceito | Equivalente na tabela |
| :--- | :--- |
| Entidade | Tabela |
| Registro | Linha |
| Atributo | Coluna |

A linguagem usada para conversar com esse banco é o **SQL** (*Structured Query Language*). Com ela é possível criar as tabelas, inserir registros, alterar dados e, principalmente, fazer consultas.

### 1.1 Transações e as propriedades ACID

Uma característica central dos bancos relacionais é o conceito de **transação**: um conjunto de operações tratado como uma unidade só. Ou tudo é aplicado, ou nada é aplicado.

O exemplo clássico é uma transferência bancária, que envolve retirar um valor de uma conta e adicionar em outra. Se o sistema falhar entre as duas operações, o dinheiro não pode simplesmente desaparecer. A transação garante que ambas aconteçam juntas ou que nenhuma aconteça.

Essa garantia é descrita pela sigla **ACID**:

| Propriedade | Significado |
| :--- | :--- |
| **Atomicidade** | A transação acontece por inteiro ou é totalmente desfeita. |
| **Consistência** | O banco sai de um estado válido para outro estado válido, respeitando as regras definidas. |
| **Isolamento** | Transações simultâneas não interferem umas nas outras. |
| **Durabilidade** | Depois de confirmada, a informação permanece salva mesmo em caso de queda do sistema. |

É por causa dessas garantias que sistemas financeiros, sistemas de matrícula e sistemas de vendas costumam usar bancos relacionais.

## 2. Chaves e Relacionamentos

Se cada entidade fica em uma tabela separada, é preciso um mecanismo para ligar uma tabela à outra. Esse mecanismo são as chaves.

### 2.1 Chave primária (PK)

A **chave primária** é a coluna que identifica cada linha de forma única dentro da tabela. Ela funciona como um documento de identidade: não se repete e não pode ficar vazia.

No PostgreSQL é comum declarar a chave primária como `SERIAL`, um tipo que gera números sequenciais automaticamente a cada inserção.

```sql
CREATE TABLE autores (
    id_autor SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nacionalidade VARCHAR(50)
);
```

### 2.2 Chave estrangeira (FK)

A **chave estrangeira** é a coluna que guarda o identificador de outra tabela, criando o vínculo entre as duas. Na tabela de livros, a coluna `id_autor` aponta para o autor que escreveu aquele livro.

```sql
CREATE TABLE livros (
    id_livro SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    genero VARCHAR(50),
    ano_publicacao INT,
    id_autor INT NOT NULL REFERENCES autores(id_autor)
);
```

A cláusula `REFERENCES autores(id_autor)` é o que declara a chave estrangeira.

### 2.3 Cardinalidade

A cardinalidade descreve quantos registros de uma tabela podem se relacionar com registros da outra.

| Tipo | Descrição | Exemplo |
| :--- | :--- | :--- |
| **1:1** | Cada registro de um lado corresponde a no máximo um do outro. | Pessoa e passaporte |
| **1:N** | Um registro de um lado pode ter vários do outro. É o caso mais comum. | Um autor tem vários livros |
| **N:N** | Vários de um lado para vários do outro. Resolvido com uma tabela associativa no meio. | Alunos e livros, ligados pela tabela de empréstimos |

### 2.4 Integridade referencial

Declarar a chave estrangeira não serve apenas para documentar a relação. O banco passa a fiscalizá-la: se houver tentativa de cadastrar um livro com um `id_autor` que não existe na tabela de autores, a operação é recusada.

Isso se chama **integridade referencial** e evita o chamado registro órfão, aquele que aponta para algo inexistente. Na prática, é o banco impedindo a entrada de dado inconsistente sem que seja preciso escrever nenhuma validação em Python.

## 3. SQL Essencial

### 3.1 SELECT e FROM

O `SELECT` define quais colunas devem aparecer no resultado, e o `FROM` indica de qual tabela os dados vêm.

```sql
SELECT titulo, genero, ano_publicacao
FROM livros;
```

O asterisco é um atalho para todas as colunas:

```sql
SELECT * FROM livros;
```

### 3.2 WHERE

O `WHERE` filtra as linhas, testando uma condição em cada uma delas e mantendo apenas aquelas em que a condição é verdadeira.

```sql
SELECT titulo, ano_publicacao
FROM livros
WHERE ano_publicacao > 1900;
```

Operadores frequentes na cláusula `WHERE`:

| Operador | Uso |
| :--- | :--- |
| `=`, `<>` | Igual, diferente |
| `>`, `<`, `>=`, `<=` | Comparações numéricas e de data |
| `BETWEEN` | Faixa de valores |
| `IN` | Pertence a uma lista |
| `LIKE` | Comparação parcial de texto |
| `IS NULL` | Testa ausência de valor |
| `AND`, `OR`, `NOT` | Combinação de condições |

### 3.3 ORDER BY e LIMIT

O `ORDER BY` ordena o resultado. O padrão é crescente (`ASC`), e `DESC` inverte para decrescente. O `LIMIT` corta o resultado em um número de linhas.

```sql
SELECT titulo, ano_publicacao
FROM livros
ORDER BY ano_publicacao DESC
LIMIT 5;
```

O `LIMIT` é especialmente útil para inspecionar uma tabela grande sem carregar todo o conteúdo.

### 3.4 JOIN

O `JOIN` combina linhas de tabelas diferentes usando a relação entre chave primária e chave estrangeira. A cláusula `ON` define a regra do encaixe.

```sql
SELECT l.titulo, a.nome AS autor
FROM livros l
JOIN autores a ON l.id_autor = a.id_autor;
```

As letras `l` e `a` são apelidos das tabelas, usados para encurtar a escrita.

Os tipos mais usados:

| Tipo | Comportamento |
| :--- | :--- |
| `INNER JOIN` (ou apenas `JOIN`) | Retorna apenas as linhas que encontram correspondência nas duas tabelas. |
| `LEFT JOIN` | Retorna todas as linhas da tabela da esquerda, mesmo as que não têm correspondência. As colunas da direita vêm como `NULL`. |
| `RIGHT JOIN` | O mesmo, invertendo o lado preservado. |
| `FULL JOIN` | Preserva as linhas dos dois lados. |

O `LEFT JOIN` combinado com `IS NULL` é um padrão frequente para encontrar registros sem correspondência, como livros que nunca foram emprestados:

```sql
SELECT li.titulo
FROM livros li
LEFT JOIN emprestimos e ON li.id_livro = e.id_livro
WHERE e.id_emprestimo IS NULL;
```

Também é possível encadear `JOIN` com três ou mais tabelas quando a informação desejada está espalhada:

```sql
SELECT al.nome AS aluno, li.titulo AS livro, e.data_emprestimo
FROM emprestimos e
JOIN alunos al ON e.id_aluno = al.id_aluno
JOIN livros li ON e.id_livro = li.id_livro;
```

### 3.5 GROUP BY, funções de agregação e HAVING

Até aqui as consultas listam linhas. O `GROUP BY` muda a natureza da pergunta: em vez de listar, ele resume.

As **funções de agregação** recebem várias linhas e devolvem um valor único:

| Função | O que calcula |
| :--- | :--- |
| `COUNT()` | Quantidade de linhas |
| `SUM()` | Soma dos valores |
| `AVG()` | Média |
| `MIN()`, `MAX()` | Menor e maior valor |

O `GROUP BY` define os grupos sobre os quais a função é aplicada, e o `HAVING` filtra esses grupos depois de formados.

```sql
SELECT a.nome, COUNT(*) AS qtd_livros
FROM autores a
JOIN livros l ON l.id_autor = a.id_autor
GROUP BY a.nome
HAVING COUNT(*) > 1
ORDER BY qtd_livros DESC;
```

A distinção entre `WHERE` e `HAVING` costuma gerar dúvida e vale registrar:

| Cláusula | Momento de atuação | O que filtra |
| :--- | :--- | :--- |
| `WHERE` | Antes do agrupamento | Linhas individuais |
| `HAVING` | Depois do agrupamento | Grupos já formados |

As duas podem aparecer na mesma consulta, cada uma no seu momento.

### 3.6 Ordem de execução

A consulta é escrita em uma ordem, mas o banco a executa em outra. Conhecer essa ordem explica por que um apelido criado no `SELECT` não pode ser usado no `WHERE`, por exemplo.

| Ordem de escrita | Ordem de execução |
| :--- | :--- |
| `SELECT` | `FROM` e `JOIN` |
| `FROM` | `WHERE` |
| `JOIN` | `GROUP BY` |
| `WHERE` | `HAVING` |
| `GROUP BY` | `SELECT` |
| `HAVING` | `ORDER BY` |
| `ORDER BY` | `LIMIT` |

## 4. Normalização

Normalização é o processo de organizar as tabelas para que cada informação seja guardada uma única vez, em um único lugar. As regras desse processo são chamadas de **formas normais**, e as três primeiras resolvem a maior parte dos casos.

### 4.1 Primeira forma normal (1FN)

Exige **valores atômicos**, ou seja, indivisíveis. Cada célula guarda um valor só.

Se um aluno possui dois telefones, eles não devem ser gravados na mesma célula separados por vírgula. A solução é criar outra linha ou uma tabela específica para telefones.

| Fora da 1FN | Dentro da 1FN |
| :--- | :--- |
| `telefones: "9999-1111, 9999-2222"` | Uma tabela `telefones` com uma linha por número |

### 4.2 Segunda forma normal (2FN)

Além de estar na 1FN, exige que todo atributo dependa da **chave inteira**, e não de apenas uma parte dela.

A regra só faz diferença quando a chave é composta, ou seja, formada por mais de uma coluna. Em uma tabela de empréstimos identificada pelo par aluno e livro, o nome do aluno depende apenas do aluno, não do par. Por isso ele não pertence a essa tabela e sim à tabela de alunos.

### 4.3 Terceira forma normal (3FN)

Além de estar na 2FN, elimina as **dependências transitivas**, que ocorrem quando uma coluna comum depende de outra coluna comum em vez de depender da chave.

O exemplo típico é guardar a nacionalidade do autor dentro da tabela de livros. A nacionalidade é uma informação do autor, não do livro. O lugar correto dela é a tabela de autores.

### 4.4 Anomalias evitadas

O trabalho de normalizar se justifica pelos problemas que ele previne. Todos nascem da mesma causa: dado repetido em vários lugares.

| Anomalia | O que acontece |
| :--- | :--- |
| **De atualização** | O dado é corrigido em um lugar e esquecido nos outros, e o banco passa a se contradizer. |
| **De exclusão** | Ao apagar uma linha, perde-se junto uma informação que só existia ali. |
| **De inserção** | Não é possível cadastrar uma informação porque outra, não relacionada, ainda não existe. |

O caminho da normalização, então, é: partir de uma tabela única e repetitiva, separar por entidades (cada assunto na sua tabela) e ligar tudo por chaves.

## 5. Conectando Python ao PostgreSQL

O SQL das seções anteriores roda dentro do banco. Em engenharia de dados, porém, quem coordena o processo é o Python, o que exige uma ponte entre os dois. Existem dois caminhos, com propostas diferentes.

### 5.1 psycopg2

O `psycopg2` é o driver oficial do PostgreSQL para Python. O caminho é direto: abre-se uma conexão e cria-se um **cursor**, que é o objeto responsável por levar os comandos até o banco e trazer a resposta.

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='biblioteca_panda',
    user='postgres',
    password='panda123',
)
cur = conn.cursor()

cur.execute('SELECT version();')
print(cur.fetchone()[0])
```

Nesse caminho o SQL é escrito manualmente, o que dá controle total sobre cada comando e sobre o momento de confirmar ou desfazer uma transação.

### 5.2 Parâmetros e SQL Injection

Quando um comando precisa receber um valor, esse valor **não deve ser concatenado** no texto do comando. O `psycopg2` usa `%s` como marcador de posição, e o valor é entregue separadamente.

```python
# Forma correta
cur.execute(
    "INSERT INTO autores (nome, nacionalidade) VALUES (%s, %s)",
    ("Machado de Assis", "Brasileira")
)

# Forma perigosa, vulnerável a SQL Injection
cur.execute(
    "INSERT INTO autores (nome) VALUES ('" + nome + "')"
)
```

O **SQL Injection** é um ataque em que alguém digita um comando SQL onde deveria entrar apenas um valor. Se o texto for concatenado, esse comando é executado pelo banco. Com o marcador de posição, a biblioteca trata o conteúdo como valor e o ataque deixa de funcionar.

### 5.3 SQLAlchemy

O `SQLAlchemy` trabalha uma camada acima. Por baixo ele usa o próprio `psycopg2`, mas oferece uma `engine` única e se integra diretamente com o pandas.

```python
from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine('postgresql+psycopg2://postgres:panda123@localhost:5432/biblioteca_panda')

# Leitura: consulta vira DataFrame
df = pd.read_sql('SELECT * FROM livros;', engine)

# Escrita: DataFrame vira tabela
df_novo.to_sql('alunos', engine, if_exists='append', index=False)
```

A string de conexão segue sempre o mesmo formato:

```text
postgresql+psycopg2://usuario:senha@host:porta/banco
```

Consultas parametrizadas também existem aqui, usando `text()` com nomes precedidos de dois pontos:

```python
with engine.connect() as connection:
    resultado = connection.execute(
        text('SELECT nome, curso FROM alunos WHERE curso = :curso'),
        {'curso': 'Engenharia de Dados'},
    )
```

### 5.4 Comparativo

| Aspecto | psycopg2 | SQLAlchemy |
| :--- | :--- | :--- |
| Nível | Driver, acesso direto | Camada sobre o driver |
| SQL | Escrito manualmente | Escrito manualmente ou gerado pelo ORM |
| Integração com pandas | Manual | `read_sql()` e `to_sql()` |
| Controle de transação | Explícito, via `commit()` e `rollback()` | Gerenciado pela `engine` |
| Indicado para | Controle fino, comando a comando | Análise em notebook, carga de DataFrames |

Na prática os dois convivem, e foi assim no roteiro desta semana: o `psycopg2` na criação das tabelas e na carga, e o `SQLAlchemy` na leitura e escrita com pandas.

### 5.5 O papel do commit

Um ponto que costuma passar despercebido: o banco trabalha como se mantivesse um rascunho. Tudo o que é escrito permanece pendente até ser confirmado com `commit()`.

```python
cur.execute("INSERT INTO alunos (nome, curso) VALUES (%s, %s)", ("Ana Souza", "Engenharia de Dados"))
conn.commit()
```

Fechar a conexão sem chamar `commit()` descarta as alterações. O oposto também existe: `rollback()` desfaz tudo o que estava pendente, o que é útil no tratamento de erros.

## 6. Introdução ao NoSQL com MongoDB (opcional)

Todo o conteúdo anterior trata do modelo relacional, em que os dados moram em tabelas de estrutura fixa. O **MongoDB** pertence à família NoSQL e organiza a informação de outra forma.

Em vez de tabelas, o MongoDB guarda **documentos**, que são estruturas no formato JSON com pares de campo e valor. Documentos ficam agrupados em **coleções**, que ocupam o papel das tabelas.

```javascript
{
  titulo: "Dom Casmurro",
  ano_publicacao: 1899,
  autor: { nome: "Machado de Assis", nacionalidade: "Brasileira" }
}
```

Duas diferenças chamam atenção nesse exemplo. A primeira é que não existe estrutura obrigatória: um documento pode ter campos que outro não tem, e a coleção aceita os dois. A segunda é que a informação do autor está aninhada dentro do próprio documento do livro, o que reduz a necessidade de `JOIN`.

| Aspecto | PostgreSQL | MongoDB |
| :--- | :--- | :--- |
| Unidade de armazenamento | Linha em uma tabela | Documento em uma coleção |
| Estrutura | Fixa, definida na criação | Flexível, por documento |
| Relacionamentos | Chaves primária e estrangeira, resolvidos com `JOIN` | Documentos aninhados ou referências |
| Consulta | SQL | Métodos como `find()` e pipelines de agregação |
| Ponto forte | Consistência e padronização | Flexibilidade e escala horizontal |

O equivalente ao `WHERE` é o filtro passado ao `find()`:

```python
db.livros.find({'ano_publicacao': {'$gt': 1900}})
```

A escolha entre os dois depende do caso: dados bem estruturados e que exigem consistência forte pedem um banco relacional; estruturas que variam muito de um registro para outro se acomodam melhor no modelo de documentos.

## 7. Prática da Semana

A prática foi desenvolvida no Google Colab e está no notebook `Semana3_Roteiro_JuliaTavares.ipynb`. O tema escolhido foi uma pequena **biblioteca universitária**, por permitir mostrar relacionamentos 1:N e N:N em um domínio simples de entender.

### 7.1 Modelo de dados

Quatro tabelas foram criadas:

```text
autores (id_autor PK)
   |
   +--< livros (id_livro PK, id_autor FK)
                  |
                  +--< emprestimos (id_emprestimo PK, id_livro FK, id_aluno FK)
                                        |
alunos (id_aluno PK) >------------------+
```

| Tabela | Papel |
| :--- | :--- |
| `autores` | Cadastro de autores, com nome e nacionalidade |
| `livros` | Acervo, com chave estrangeira para o autor |
| `alunos` | Cadastro de alunos, com nome e curso |
| `emprestimos` | Liga aluno e livro, com as datas de empréstimo e devolução |

A tabela `emprestimos` é a tabela associativa que resolve o relacionamento N:N entre alunos e livros, já que um aluno pode pegar vários livros e um livro pode ser emprestado a vários alunos ao longo do tempo.

### 7.2 Preparação do ambiente

O Colab roda sobre uma máquina virtual Ubuntu, o que permite instalar o PostgreSQL na própria sessão. Isso dispensa qualquer instalação local.

```python
!sudo apt-get -y -qq update
!sudo apt-get -y -qq install postgresql postgresql-contrib
!sudo service postgresql start

!sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'panda123';"
!sudo -u postgres psql -c "CREATE DATABASE biblioteca_panda;"
```

```python
!pip install -q sqlalchemy psycopg2-binary pandas
```

Vale registrar que esse banco **não é persistente**: se a sessão do Colab reiniciar, todas as células precisam ser executadas novamente, em ordem.

### 7.3 Criação das tabelas

```python
cur.execute("""
    DROP TABLE IF EXISTS emprestimos CASCADE;
    DROP TABLE IF EXISTS livros CASCADE;
    DROP TABLE IF EXISTS alunos CASCADE;
    DROP TABLE IF EXISTS autores CASCADE;

    CREATE TABLE autores (
        id_autor SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        nacionalidade VARCHAR(50)
    );

    CREATE TABLE livros (
        id_livro SERIAL PRIMARY KEY,
        titulo VARCHAR(150) NOT NULL,
        genero VARCHAR(50),
        ano_publicacao INT,
        id_autor INT NOT NULL REFERENCES autores(id_autor)
    );

    CREATE TABLE alunos (
        id_aluno SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        curso VARCHAR(80) NOT NULL
    );

    CREATE TABLE emprestimos (
        id_emprestimo SERIAL PRIMARY KEY,
        id_livro INT NOT NULL REFERENCES livros(id_livro),
        id_aluno INT NOT NULL REFERENCES alunos(id_aluno),
        data_emprestimo DATE NOT NULL,
        data_devolucao DATE
    );
""")
conn.commit()
```

O `DROP TABLE IF EXISTS` no início permite reexecutar o notebook do zero sem erro de tabela já existente. A ordem das exclusões respeita as dependências: as tabelas que apontam para outras são removidas primeiro.

A criação pode ser conferida consultando o catálogo do próprio banco:

```python
cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public' ORDER BY table_name;
""")
for (nome,) in cur.fetchall():
    print('-', nome)
```

**Saída:**

```text
- alunos
- autores
- emprestimos
- livros
```

### 7.4 Inserção de dados com Python

A carga usa `executemany()`, que insere várias linhas de uma vez, sempre com valores parametrizados.

```python
autores = [
    ('Machado de Assis', 'Brasileira'),
    ('Clarice Lispector', 'Brasileira'),
    ('George Orwell', 'Britânica'),
    ('Jane Austen', 'Britânica'),
]
cur.executemany('INSERT INTO autores (nome, nacionalidade) VALUES (%s, %s)', autores)

livros = [
    ('Dom Casmurro', 'Romance', 1899, 1),
    ('Memórias Póstumas de Brás Cubas', 'Romance', 1881, 1),
    ('A Hora da Estrela', 'Romance', 1977, 2),
    ('Laços de Família', 'Contos', 1960, 2),
    ('1984', 'Ficção Científica', 1949, 3),
    ('A Revolução dos Bichos', 'Fábula', 1945, 3),
    ('Orgulho e Preconceito', 'Romance', 1813, 4),
]
cur.executemany(
    'INSERT INTO livros (titulo, genero, ano_publicacao, id_autor) VALUES (%s, %s, %s, %s)',
    livros,
)

conn.commit()
```

Conferindo a carga:

```python
for t in ['autores', 'livros', 'alunos', 'emprestimos']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t:<13} -> {cur.fetchone()[0]} registros')
```

**Saída:**

```text
autores       -> 4 registros
livros        -> 7 registros
alunos        -> 4 registros
emprestimos   -> 7 registros
```

### 7.5 Consultas básicas

```python
import pandas as pd

query = """
    SELECT titulo, genero, ano_publicacao
    FROM livros
    WHERE ano_publicacao > 1900
    ORDER BY ano_publicacao DESC;
"""
pd.read_sql(query, conn)
```

**Saída:**

| | titulo | genero | ano_publicacao |
|---|---|---|---|
| 0 | A Hora da Estrela | Romance | 1977 |
| 1 | Laços de Família | Contos | 1960 |
| 2 | 1984 | Ficção Científica | 1949 |
| 3 | A Revolução dos Bichos | Fábula | 1945 |

### 7.6 Consultas intermediárias

Livro com o nome do autor, usando a relação entre chave primária e chave estrangeira:

```python
query = """
    SELECT l.titulo, l.genero, a.nome AS autor
    FROM livros l
    JOIN autores a ON l.id_autor = a.id_autor
    ORDER BY a.nome;
"""
pd.read_sql(query, conn)
```

Total de empréstimos por curso, cruzando três informações e agrupando:

```python
query = """
    SELECT al.curso, COUNT(*) AS total_emprestimos
    FROM emprestimos e
    JOIN alunos al ON e.id_aluno = al.id_aluno
    GROUP BY al.curso
    ORDER BY total_emprestimos DESC;
"""
pd.read_sql(query, conn)
```

**Saída:**

| | curso | total_emprestimos |
|---|---|---|
| 0 | Engenharia de Dados | 3 |
| 1 | Ciência da Computação | 2 |
| 2 | Estatística | 2 |

Livros que nunca foram emprestados, com `LEFT JOIN` e teste de nulo:

```python
query = """
    SELECT li.titulo
    FROM livros li
    LEFT JOIN emprestimos e ON li.id_livro = e.id_livro
    WHERE e.id_emprestimo IS NULL;
"""
pd.read_sql(query, conn)
```

Autores com mais de um livro no acervo, com `GROUP BY` e `HAVING`:

```python
query = """
    SELECT a.nome, COUNT(l.id_livro) AS qtd_livros
    FROM autores a
    JOIN livros l ON a.id_autor = l.id_autor
    GROUP BY a.nome
    HAVING COUNT(l.id_livro) > 1;
"""
pd.read_sql(query, conn)
```

**Saída:**

| | nome | qtd_livros |
|---|---|---|
| 0 | Machado de Assis | 2 |
| 1 | Clarice Lispector | 2 |
| 2 | George Orwell | 2 |

### 7.7 Leitura e escrita com SQLAlchemy

Depois de trabalhar com `psycopg2`, o notebook repete as operações pelo `SQLAlchemy`, dessa vez integrando com o pandas.

```python
from sqlalchemy import create_engine, text

engine = create_engine('postgresql+psycopg2://postgres:panda123@localhost:5432/biblioteca_panda')

# Leitura
df_alunos = pd.read_sql('SELECT * FROM alunos;', engine)
```

```python
# Escrita: um DataFrame vira novas linhas na tabela
novos_alunos = pd.DataFrame([
    {'nome': 'Elisa Prado', 'curso': 'Engenharia de Dados'},
    {'nome': 'Felipe Rocha', 'curso': 'Ciência da Computação'},
])
novos_alunos.to_sql('alunos', engine, if_exists='append', index=False)
```

O parâmetro `if_exists` merece atenção: `append` acrescenta linhas, `replace` apaga a tabela e a recria, e `fail` gera erro se a tabela já existir. O valor padrão é `fail`.

### 7.8 Normalização aplicada ao exemplo

Para tornar o conceito concreto, o notebook monta a versão desnormalizada do mesmo conjunto de dados:

```python
desnormalizada = pd.DataFrame([
    {'aluno': 'Ana Souza', 'curso': 'Engenharia de Dados', 'livro': 'Dom Casmurro', 'autor': 'Machado de Assis'},
    {'aluno': 'Ana Souza', 'curso': 'Engenharia de Dados', 'livro': 'A Hora da Estrela', 'autor': 'Clarice Lispector'},
    {'aluno': 'Bruno Lima', 'curso': 'Ciência da Computação', 'livro': '1984', 'autor': 'George Orwell'},
])
```

O nome e o curso de Ana Souza se repetem a cada empréstimo. Se o curso dela mudar, será preciso alterar várias linhas, e basta esquecer uma para o banco passar a informar dois cursos diferentes para a mesma pessoa.

No modelo normalizado, nome e curso existem em um único lugar, a tabela `alunos`, e a tabela `emprestimos` guarda apenas as chaves estrangeiras e as datas.

### 7.9 Versão em MongoDB (opcional)

A parte final do notebook repete uma carga simples no MongoDB, usando `mongomock` para simular o banco sem exigir servidor.

```python
!pip install -q pymongo mongomock
import mongomock

client = mongomock.MongoClient()
db = client['biblioteca_panda']

db.livros.insert_many([
    {'titulo': 'Dom Casmurro', 'ano_publicacao': 1899,
     'autor': {'nome': 'Machado de Assis', 'nacionalidade': 'Brasileira'}},
    {'titulo': '1984', 'ano_publicacao': 1949,
     'autor': {'nome': 'George Orwell', 'nacionalidade': 'Britânica'}},
])

list(db.livros.find({'ano_publicacao': {'$gt': 1900}}))
```

Para usar um banco real, basta trocar `mongomock.MongoClient()` por `pymongo.MongoClient()` apontando para um cluster do MongoDB Atlas, que tem camada gratuita.

## 8. Boas Práticas

**Faça**

- Use marcadores de posição (`%s` no psycopg2, `:nome` no SQLAlchemy) em todo comando que receba valores vindos de fora.
- Defina chave primária em toda tabela e declare as chaves estrangeiras nos relacionamentos, deixando o banco fiscalizar a consistência.
- Confirme as escritas com `commit()` e feche cursor e conexão ao terminar, já que conexões abertas consomem recursos do servidor.
- Normalize o modelo antes de carregar os dados, porque reorganizar depois custa muito mais.
- Nomeie tabelas e colunas de forma padronizada, em minúsculas e sem acentos, evitando a necessidade de aspas nas consultas.
- Guarde senhas e strings de conexão em variáveis de ambiente, nunca escritas direto no notebook.

**Evite**

- Montar comandos SQL concatenando valores em texto, prática que abre caminho para SQL Injection.
- Repetir a mesma informação em várias tabelas, o que gera as anomalias descritas na seção de normalização.
- Executar `UPDATE` ou `DELETE` sem cláusula `WHERE`, já que sem o filtro o comando atinge a tabela inteira e não existe desfazer.
- Consultar tabelas grandes com `SELECT *` sem `LIMIT` quando o objetivo é apenas inspecionar o conteúdo.
- Deixar transações abertas sem `commit()` ou `rollback()`, situação que pode manter registros bloqueados para outras operações.

## 9. Conclusão

Esta semana percorreu o caminho completo entre teoria e prática do modelo relacional. Partindo do conceito de tabela, passando por chaves e relacionamentos, foi possível construir um banco com quatro entidades ligadas entre si e consultá-lo com SQL, das operações básicas de filtro e ordenação até cruzamentos com `JOIN` e resumos com `GROUP BY`.

A normalização apareceu não como regra abstrata, mas como resposta a problemas concretos: o mesmo conjunto de dados foi montado nas versões desnormalizada e normalizada, deixando visível o que se ganha ao separar as entidades.

Na ponte com o Python, os dois caminhos foram exercitados. O `psycopg2` mostrou o controle direto sobre comandos e transações, e o `SQLAlchemy` mostrou a integração com o pandas que torna prática a análise em notebook. Os dois se apoiam no mesmo cuidado com parâmetros, que é o que protege o banco de SQL Injection.

Por fim, o contraste com o MongoDB serviu para situar o modelo relacional entre as alternativas existentes, deixando claro que a escolha do banco depende da natureza dos dados e das garantias necessárias.

O banco construído aqui é a base natural para as próximas semanas, quando o assunto passa a ser modelagem de dados e, mais adiante, a organização analítica em Data Warehouse.

## 10. Glossário

| Termo | Definição |
| :--- | :--- |
| **SGBD** | Sistema Gerenciador de Banco de Dados, o software que administra o banco. O PostgreSQL é um deles. |
| **SQL** | Linguagem padrão para criar, alterar e consultar dados em bancos relacionais. |
| **Tabela** | Estrutura que representa uma entidade, organizada em linhas e colunas. |
| **Registro** | Uma linha da tabela, correspondente a uma ocorrência da entidade. |
| **Atributo** | Uma coluna da tabela, correspondente a uma característica da entidade. |
| **Chave primária (PK)** | Coluna que identifica cada linha de forma única. |
| **Chave estrangeira (FK)** | Coluna que referencia a chave primária de outra tabela, criando o relacionamento. |
| **Cardinalidade** | Quantidade de registros que podem se relacionar entre duas tabelas (1:1, 1:N, N:N). |
| **Integridade referencial** | Garantia de que uma chave estrangeira sempre aponta para um registro existente. |
| **Tabela associativa** | Tabela intermediária que resolve um relacionamento N:N. |
| **Transação** | Conjunto de operações tratado como unidade indivisível. |
| **ACID** | Atomicidade, Consistência, Isolamento e Durabilidade, as garantias de uma transação. |
| **Commit** | Comando que confirma as alterações pendentes de uma transação. |
| **Rollback** | Comando que desfaz as alterações pendentes de uma transação. |
| **JOIN** | Operação que combina linhas de tabelas diferentes segundo uma condição. |
| **Função de agregação** | Função que resume várias linhas em um valor, como `COUNT`, `SUM` e `AVG`. |
| **Normalização** | Processo de organizar tabelas para eliminar redundância e anomalias. |
| **Valor atômico** | Valor indivisível, exigência da primeira forma normal. |
| **Dependência transitiva** | Situação em que um atributo depende de outro atributo não chave, eliminada na 3FN. |
| **Cursor** | Objeto que executa comandos no banco e recupera os resultados. |
| **Driver** | Biblioteca que permite a uma linguagem se comunicar com um SGBD, como o `psycopg2`. |
| **Engine** | Objeto do SQLAlchemy que encapsula a conexão com o banco. |
| **SQL Injection** | Ataque em que comandos maliciosos são inseridos onde deveriam entrar apenas valores. |
| **NoSQL** | Conjunto de bancos que não seguem o modelo relacional. |
| **Documento** | Registro do MongoDB, no formato JSON, equivalente a uma linha. |
| **Coleção** | Agrupamento de documentos no MongoDB, equivalente a uma tabela. |

## 11. Materiais Complementares

- [Introdução a Bancos de Dados Relacionais, IBM](https://www.ibm.com/topics/relational-databases)
- [SQL Tutorial, W3Schools](https://www.w3schools.com/sql/)
- [PostgreSQL e Python com psycopg2, GeeksforGeeks](https://www.geeksforgeeks.org/postgresql-connecting-to-the-database-using-python/)
- [SQLAlchemy, primeiros passos](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Normalização de dados, GeeksforGeeks](https://www.geeksforgeeks.org/introduction-of-database-normalization/)
- [Introdução ao MongoDB](https://www.mongodb.com/docs/manual/introduction/)
- [Documentação oficial do PostgreSQL](https://www.postgresql.org/docs/)

## 12. Entrega da Semana

**Atividade proposta**

Criar uma base PostgreSQL, definir tabelas simples com suas chaves, inserir dados usando Python e executar consultas SQL básicas e intermediárias.

**Tempo sugerido:** de 60 a 90 minutos.

**Formato aceito**, à escolha de quem entrega:

- capturas de tela das tabelas e das consultas executadas no PostgreSQL; ou
- notebook com a conexão funcional entre Python e PostgreSQL, contendo a carga dos dados e as consultas.

**Checklist do que deve constar**

- [x] Base PostgreSQL criada
- [x] Tabelas com chave primária e chave estrangeira
- [x] Dados inseridos por meio de Python
- [x] Consultas básicas com `SELECT`, `WHERE` e `ORDER BY`
- [x] Consultas intermediárias com `JOIN` e `GROUP BY`
- [x] Conexão testada com `psycopg2` ou `SQLAlchemy`
- [x] Leitura e escrita verificadas entre Python e o banco
- [x] Opcional: mesmas operações reproduzidas no MongoDB

**Arquivos desta entrega**

```text
Semana3_Julia_Tavares/
├── Semana 03.md                                  resumo desta semana
├── Semana3_Slides_JuliaTavares.pptx              apresentação teórica
├── Semana3_Roteiro_JuliaTavares.ipynb            roteiro prático do Colab
├── Semana3_Roteiro_Apresentacao_JuliaTavares.docx  roteiro de fala do vídeo
└── Semana3_Apresentacao_JuliaTavares_editado.mp4   vídeo da apresentação
```
