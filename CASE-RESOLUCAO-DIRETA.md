# Case "Rede Aurora" — resolução direta

> Resposta comentada do case, sem enunciado passo a passo nem espaço para
> anotar — é o material para revisar rápido antes de uma entrevista real, tipo
> README. Nenhum conteúdo novo: é o mesmo `CASE-processo-seletivo-com-gabarito.md`
> reorganizado em formato direto — pergunta, resposta, ponto de atenção.
>
> Lembrete que vale para o case inteiro: **não existe resposta única.** O que
> segue é o raciocínio esperado, não um molde a decorar. O que se avalia é
> como a pessoa pensa, o que pergunta antes de responder, e se enxerga o que
> vai dar errado.

---

## Contexto

**Rede Aurora** — 40 lojas físicas + venda online. A diretoria quer um
**painel diário de vendas**, atualizado toda manhã antes das 8h, respondendo:

1. Quanto a rede vendeu ontem, por loja e por categoria de produto?
2. Quais produtos em promoção venderam mais que o normal?
3. Qual o percentual de pedidos online entregues no prazo?

Hoje ninguém responde as três juntas — os dados estão em três lugares:

| Fonte | Natureza |
|---|---|
| **PDV (ponto de venda)** | PostgreSQL de produção, atualizado a cada venda no caixa. Tabelas `pedido`, `item_pedido`, `produto`, `loja`. ~80 mil itens/dia. Mesmo banco que os caixas usam em tempo real. |
| **Planilha de promoções** | Preenchida à mão pelo marketing: produto, % desconto, início/fim. "Atualizada toda segunda" — na prática, às vezes só na quarta. Colunas mudam de nome. Já apareceu `10%` numa célula e `0,10` em outra. |
| **API do parceiro de entrega** | Status por pedido: `em_separacao`, `a_caminho`, `entregue`, `devolvido`, com data de cada mudança. **Corrige retroativamente** até **7 dias atrás**. Pagina em **500 registros**, limite de **60 chamadas/min**. |

---

## Bloco 0 — Antes de desenhar

**Pergunta:** quais perguntas você faria antes de escrever qualquer linha de código? Liste pelo menos quatro.

**O que se avalia:** se a pessoa desenha antes de entender. Separa mais candidatos do que qualquer outro bloco, e é o mais ignorado.

**Resposta — perguntas que precisam de resposta antes do desenho:**

| Pergunta | Por que importa |
|---|---|
| Posso ler o banco de produção diretamente? | Quase sempre "prefira que não" — muda a arquitetura inteira |
| O que conta como "venda de ontem": pedido feito, pago, ou entregue? | Sem isso, marketing e financeiro veem números diferentes e culpam o pipeline |
| Qual o fuso horário do "ontem"? O que acontece com uma venda às 23h58? | Fronteira de data é a fonte silenciosa de erro mais comum em relatório diário |
| O painel precisa de histórico ou só do dia anterior? | Determina se você guarda série ou sobrescreve |
| Pedido cancelado ou devolvido conta como venda? | Regra de negócio que muda o número final |
| Quem é dono da planilha, e ela pode ganhar coluna nova sem aviso? | Determina o quão defensiva a ingestão precisa ser |

**Armadilha:** ir direto para "eu usaria Airflow com três DAGs". Ferramenta antes de requisito é o erro clássico.

**Diferencial:** perguntar *"esse número vai ser usado para decidir o quê?"* — um painel que orienta reposição de estoque tolera aproximação; um que alimenta comissão de vendedor, não.

---

## Bloco 1 — Arquitetura

**Pergunta:** desenhe o fluxo de ponta a ponta, das três fontes até o painel. Diga o que roda quando.

**O que se avalia:** se a pessoa trata fontes de naturezas diferentes de formas diferentes.

**Resposta:**

```
PDV (PostgreSQL producao) --> extracao incremental por janela de data,
                               fora do horario de pico, de uma REPLICA
                               (ou via CDC, se existir)

Planilha de promocoes ------> ingestao defensiva: valida colunas, tipos
                               e faixas ANTES de qualquer coisa

API de entrega --------------> paginacao (500/pagina) + controle de ritmo
                                (60 req/min) + retry com backoff
                                janela movel de 8 dias, por causa da correcao
                    |
                    v
              data/raw/  (bronze - exatamente como chegou, por data)
                    |
                    v
              validacao  --> quarentena (com o motivo da rejeicao)
                    |
                    v
              transformacao (silver - tipado, padronizado, deduplicado)
                    |
                    v
              fato + dimensoes no Data Warehouse (gold)
                    |
                    v
              painel

  Orquestracao: uma DAG diaria, disparada as 04h para dar folga ate as 8h.
```

- **Não ler o banco de produção diretamente.** O relatório varre milhões de linhas e compete com os caixas. Réplica de leitura, ou CDC. No mínimo: janela restrita, fora de pico, colunas específicas — nunca `SELECT *`.
- **Extração incremental, não full.** 80 mil itens/dia acumulam — puxar só a janela nova.
- **Janela de 8 dias para a API de entrega**, não de 1 — ela corrige até 7 dias atrás. Quem puxa só o dia anterior nunca vê as correções, e "entregue no prazo" fica permanentemente errado.

**Armadilha:** tratar as três fontes com o mesmo padrão de ingestão. Garantias completamente diferentes: PDV confiável e estruturado; planilha sem garantia nenhuma; API confiável mas muda o passado.

**Diferencial:** as três podem ser **três DAGs independentes** convergindo numa quarta de consolidação — para que a falha da planilha não impeça a carga das vendas.

---

## Bloco 2 — Modelo de dados

**Pergunta:** qual é a granularidade da sua tabela fato? Quais dimensões existem? Por quê?

**O que se avalia:** granularidade, e se a pessoa sabe que é uma decisão sem volta.

**Resposta — granularidade: um item de pedido, não um pedido.** Motivo: a pergunta 1 do enunciado é "por categoria de produto". Se a granularidade fosse por pedido, um pedido com um fone e uma capa teria uma categoria só (ou nenhuma) — impossível de responder, e corrigir exigiria reprocessar todo o histórico.

```
fato_venda_item   (grao: 1 item de 1 pedido)
+-- sk_data           FK -> dim_data
+-- sk_loja           FK -> dim_loja
+-- sk_produto        FK -> dim_produto
+-- sk_canal          FK -> dim_canal        (loja fisica / site)
+-- sk_promocao       FK -> dim_promocao     (ou "sem promocao")
+-- id_pedido                                (chave natural, para rastrear)
+-- quantidade
+-- valor_unitario
+-- valor_desconto
`-- valor_total

Dimensoes: dim_data, dim_loja, dim_produto (com categoria e
subcategoria), dim_canal, dim_promocao.
```

- **Status de entrega não é medida** e não pertence à `fato_venda_item` — pertence ao pedido, não ao item, e muda com o tempo. Saída limpa: uma segunda fato, `fato_entrega`, grão de um pedido online, guardando a data de cada status. Dizer que status de entrega é medida da venda é o erro mais comum deste bloco.
- **Surrogate key (`sk_`):** o código do produto pode ser renumerado pelo fornecedor, e o mesmo produto pode vir do PDV e do site com códigos diferentes. Sem chave artificial, SCD Tipo 2 é impossível.

**Diferencial:** `dim_produto` precisa de **SCD Tipo 2** para a categoria. Se um produto muda de categoria e a dimensão sobrescrever, todo o histórico de vendas dele muda de categoria retroativamente — e um relatório de trimestre já apresentado passa a mostrar outro número sem que nenhuma venda tenha mudado.

---

## Bloco 3 — Qualidade

**Pergunta:** onde ficam as validações? O que acontece com um registro reprovado?

**O que se avalia:** se a pessoa separa detectar de corrigir, e pensa no destino do que reprova.

**Resposta — validações por fonte, porque os riscos são diferentes:**

| Fonte | O que validar |
|---|---|
| PDV | Contagem bate com a origem · sem pedido órfão · `valor_total ≈ quantidade × valor_unitario − desconto` · datas dentro da janela esperada |
| Planilha | Colunas esperadas existem (falha se não) · desconto numérico entre 0 e 1 (ou 0 e 100 — escolher uma e normalizar) · `data_fim ≥ data_inicio` · produto existe no cadastro |
| API | Status pertence ao conjunto conhecido · sem `id_pedido` duplicado no mesmo lote · pedido existe na fato de vendas |

- **Registro reprovado → quarentena, não descarte.** Vai para área separada com o motivo. Razão estatística: 200 registros rejeitados pela mesma regra quase nunca são 200 dados ruins — são um bug na regra ou uma mudança na fonte.
- **A armadilha de ouro — `10%` vs `0,10`:** não é conversão, é ambiguidade genuína. `0,10` pode ser 10% como fração ou 0,10% digitado errado. Define-se uma regra explícita (ex.: valor ≤ 1 é fração), documenta-se, e qualquer valor fora de faixa plausível (acima de 90% de desconto) vai para quarentena com aviso. Adivinhar em silêncio é o relatório mentir.

**Diferencial:** propor uma **validação de reconciliação** — comparar a soma do faturamento do dia com o total que o próprio PDV reporta. "Carregou sem erro" não é "carregou tudo". É a checagem que pega o caso mais perigoso: pipeline que roda com sucesso e traz metade dos dados.

---

## Bloco 4a — Operação: a planilha atrasou

**Pergunta:** a planilha do marketing não foi preenchida na segunda. O pipeline para ou continua? Justifique.

**O que se avalia:** se a pessoa entende que isso **não é decisão técnica**.

**Resposta:** depende de qual pergunta o painel precisa responder naquele dia. A pergunta 1 (vendas por loja/categoria) não depende da planilha — travar o painel inteiro penaliza a diretoria por um atraso do marketing. A pergunta 2 (produtos em promoção) depende inteiramente dela.

- **Portanto: o pipeline continua**, carrega as vendas normalmente, e o painel exibe de forma visível que a informação de promoções está desatualizada, com a data da última atualização. Em paralelo, alerta para o marketing.
- A distinção técnica: ausência da planilha é **problema de qualidade** (registrado, tratado, segue), não **erro estrutural** (para). Seria erro estrutural se a planilha existisse sem as colunas obrigatórias.
- Sutileza: "sem promoção cadastrada" e "promoção ainda não preenchida" são estados diferentes — não podem virar o mesmo `NULL`, ou o relatório afirma que não houve promoção numa semana em que houve.

**Armadilha:** responder só "continua" ou só "para" — meia resposta. A resposta completa é continua + sinaliza + alerta, com a regra combinada antes com quem usa o painel.

---

## Bloco 4b — Operação: correções sem duplicar

**Pergunta:** o parceiro corrige status de até 7 dias atrás. Como o painel reflete a correção sem duplicar nada?

**O que se avalia:** **idempotência** — a pergunta mais difícil do case. *(Não estava no material do PANDA; três pessoas do grupo chegaram lá sozinhas, construindo.)*

**Resposta, em três partes:**

1. **Janela de extração móvel, de 8 dias.** Não adianta buscar só ontem — as correções chegam para trás. Todo dia o pipeline rebusca os últimos 8 dias (7 de correção + 1 de folga).
2. **A carga é um `upsert` por chave natural** (`id_pedido`), não um `insert`:

```sql
INSERT INTO fato_entrega (id_pedido, status, data_status, atualizado_em)
VALUES (...)
ON CONFLICT (id_pedido) DO UPDATE
  SET status        = EXCLUDED.status,
      data_status   = EXCLUDED.data_status,
      atualizado_em = NOW();
```

   Rodar isso dez vezes com o mesmo lote produz o mesmo resultado que rodar uma vez — isso é idempotência, e é o que torna seguro reprocessar.

3. **As agregações dos últimos 8 dias precisam ser recalculadas**, não só as de ontem. Corrigir a linha na fato não adianta se a Gold do dia 3 continuar com o número velho.

**Armadilha:** `DELETE` da janela seguido de `INSERT`. Funciona, mas cria uma janela de tempo em que o dado não existe — se a carga falhar no meio, apaga o dado bom e não coloca o novo. Se usar essa estratégia, precisa estar dentro de uma transação.

**Diferencial:** guardar `atualizado_em` na linha — a correção retroativa é uma dimensão que muda lentamente disfarçada. Se alguém precisar auditar "o que o painel mostrava na terça passada", só o histórico de versões responde.

---

## Bloco 5 — Trade-offs

**Pergunta:** o que na sua solução vai quebrar primeiro quando a rede dobrar de tamanho? O que você faria diferente se o painel precisasse estar atualizado a cada 5 minutos em vez de uma vez por dia?

**O que se avalia:** se a pessoa enxerga o limite da própria solução — não se espera escala infinita, espera-se saber onde ela quebra.

**a) O que quebra primeiro, em ordem provável:**

1. **A extração do PDV.** 160 mil itens/dia de um banco de produção é o gargalo mais próximo. Solução: réplica dedicada, ou CDC.
2. **A janela de tempo.** A DAG das 4h precisa terminar antes das 8h — dobrar o volume pode estourar. Solução: paralelizar por loja, ou antecipar o horário.
3. **As agregações recalculando 8 dias inteiros.** Solução: particionar a fato por data, reprocessar só as partições afetadas.
4. **A planilha.** Não escala nada — mais rede é mais promoção, mais linha, mais erro humano. Solução real não é técnica: substituir a planilha por um cadastro com validação na entrada.

**b) Painel a cada 5 minutos?** Resposta forte começa questionando o requisito: quem precisa de venda com 5 minutos de atraso, e que decisão toma com isso? Se a resposta for "nenhuma, seria bom ter", o custo não se justifica.

| Componente | Batch diário | A cada 5 minutos |
|---|---|---|
| PDV | extração por janela | CDC lendo o log de transações |
| Transporte | arquivo | tópico de eventos (Kafka) |
| Processamento | pandas | stream, ou micro-batch |
| Fato | recarga da janela | upsert contínuo — idempotência vira obrigação, não conveniência |
| Promoções | planilha diária | tabela de referência em cache — não precisa tempo real |
| Entregas | janela de 8 dias | continua batch — correção retroativa não é evento em tempo real |

**Diferencial:** perceber que **nem tudo precisa mudar de ritmo.** Só a venda precisa ser rápida; promoção muda uma vez por semana; correção de entrega é retroativa por natureza. Arquitetura híbrida — stream para venda, batch para o resto — é mais barata e mais simples que converter tudo. "Eu colocaria Kafka em tudo" é a resposta que parece avançada e é a errada.

---

## Como o case costuma ser avaliado

| Critério | O que se observa | Peso |
|---|---|---|
| Faz perguntas antes de responder | Bloco 0 — quem desenha antes de entender já perdeu | alto |
| Granularidade justificada | Escolheu item e disse por quê, ligando à pergunta de negócio | alto |
| Trata fontes diferentes de formas diferentes | Não aplica o mesmo padrão às três | médio |
| Idempotência | Resolveu 4b sem duplicar e sem apagar | alto |
| Separa decisão técnica de decisão de negócio | Bloco 4a | médio |
| Sabe onde a própria solução quebra | Bloco 5a | médio |
| Não superdimensiona | Não põe Kafka onde cabe um cron | médio |
| Comunica o raciocínio | Pensa em voz alta, assume premissas explicitamente | alto |

---

## De onde cada bloco veio (mapa para o curso)

| Bloco | Semanas que preparam | Observação |
|---|---|---|
| 0 — Esclarecer | S5, S7 | Regra de negócio explícita e documentada |
| 1 — Arquitetura | S2, S6, S7 | Paginação, rate limit, DAG, camadas |
| 2 — Modelo | S3, S4, S7 | PK/FK, fato/dimensão, granularidade, SCD |
| 3 — Qualidade | S5 | Validar ≠ transformar; quarentena |
| 4a — Parar ou seguir | S5 | Erro estrutural × problema de qualidade |
| 4b — Retroatividade | S3 (ACID) + S6 (retry) | Idempotência — não está no material do PANDA |
| 5 — Trade-offs | S2, S6, S7 | Batch × streaming; onde a escala quebra |

> Se você chegou na palavra **idempotência** sem ela ter sido ensinada, você entendeu a aula.

---

**Fonte de referência para o formato do case:** Data Engineer Case Study Interview Questions + Guide — Interview Query (interviewquery.com/p/data-engineer-case-study) — estrutura de avaliação, categorias de pergunta e forma esperada de resposta.
**Material original completo (enunciado + gabarito em leitura corrida):** `CASE-processo-seletivo-com-gabarito.md`, no repositório do grupo.
