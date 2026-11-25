# Validador de voos de drone de entrega: AP + ALL

Trabalho prático de **Linguagens Formais e Autômatos**: reconhecimento de linguagens com pilha e fita limitada.

Um drone sai da base, faz uma rota até o ponto de entrega e precisa **voltar refazendo o caminho ao contrário**. Ao fim do voo, as **duas caixas-pretas** (principal e reserva) precisam ter registrado **os mesmos eventos**. A validação tem duas etapas:

| Etapa | Reconhecedor | O que verifica | Classe da linguagem |
|---|---|---|---|
| 1 | **AP** (autômato de pilha) | estrutura `B w E inv(w) B # x \| y`: a volta desfaz a ida (último movimento desfeito primeiro, com a direção oposta) | livre de contexto, **não regular** |
| 2 | **ALL** (autômato linearmente limitado) | o trecho após `#`: o registro reserva `y` é uma **permutação** do principal `x` (mesmas quantidades de cada evento) | sensível ao contexto, **não livre de contexto** |

O ALL só roda se o AP aceitar.

**Painel interativo online:** https://andreyyrson.github.io/validador-drone-ap-all/web/. Pilote o drone, rode os cenários ou jogue o modo desafio direto no navegador.

### Alfabeto

| Símbolo | Significado |
|---|---|
| `B` | base (partida e chegada) |
| `N` `S` `L` `O` | movimentos Norte, Sul, Leste e Oeste (opostos: N↔S, L↔O) |
| `E` | ponto de entrega (meio da rota) |
| `#` | separa a rota dos registros |
| `g` `a` `v` | eventos: leitura de GPS, alerta de bateria, rajada de vento |
| `\|` | separa o registro principal do reserva |

Exemplo: `BNLLNESOOSB#gvag|aggv`. A ida é `NLLN` e a volta é `SOOS` (o último `N` é desfeito primeiro, por um `S`). O reserva `aggv` tem os mesmos eventos de `gvag`: 2 `g`, 1 `v` e 1 `a`.

## Instalar

Requer **Python 3.8+**. Não há dependências externas, só a biblioteca padrão.

```bash
git clone https://github.com/andreyyrson/validador-drone-ap-all.git
cd validador-drone-ap-all
```

> No Windows, use `python` no lugar de `python3`.

## Executar

### Painel interativo (para a apresentação e para o professor usar)

```bash
python3 visualizador.py        # exporta as tabelas δ para web/automatos.js e abre web/index.html
```

Não precisa de servidor nem de instalação: `web/index.html` também abre com duplo clique e pode ser publicado no GitHub Pages (Settings → Pages → branch `main`, pasta raiz). Este repositório já está publicado em https://andreyyrson.github.io/validador-drone-ap-all/web/.

| Modo | Como usar |
|---|---|
| **Pilotar** | Conduza o drone pelas setas do teclado (↑ N, ↓ S, → L, ← O) ou pelos botões. As teclas `B` e `E` marcam base e entrega; `#`, `g`, `a`, `v` e `\|` montam as caixas-pretas. O AP roda a cada comando: a pilha cresce e diminui ao vivo, a seta verde mostra o movimento que o topo exige, um movimento inválido aparece na hora com ✕ e `⌫` desfaz o último comando. |
| **Replay** | `Enter` ou **▶ Validar missão** anima a validação completa. Nela, a fita do ALL é marcada com `X` célula por célula, e o evento em trânsito aparece como "memória do estado". Controles: `espaço`, `← →`, `Home`/`End`. As missões prontas trazem os três cenários de integração. |
| **Desafio** | O painel sorteia uma missão. A pessoa prevê *Aceita*, *Rejeita no AP* ou *Rejeita no ALL* (teclas 1, 2 e 3) e a animação mostra por quê. O placar fica na tela. |

A **visão de compilador**, embaixo, mostra a mesma missão passando pelas fases de um compilador:
1. análise léxica (tokens);
2. análise sintática = AP, com a árvore de derivação;
3. análise semântica = ALL;
4. geração de código para o drone, com otimização peephole.

O painel executa as mesmas tabelas δ do Python com `web/simulador.js`. O `testes.py` confere, no Node, que o JS produz rastreamentos e compilações idênticos aos do Python.

### Visão de compilador no terminal

```bash
python3 compilador.py "BNLLNESOOSB#gvag|aggv"   # tokens, árvore de derivação, semântica e código gerado
```

### Linha de comando

```bash
# fluxo completo (AP e depois ALL), com os rastreamentos dos dois autômatos
python3 main.py "BNLLNESOOSB#gvag|aggv"

# os três cenários obrigatórios de integração, em sequência
python3 main.py --demo

# só um reconhecedor
python3 main.py --modulo ap  "BNLLNESOOSB#gvag|aggv"
python3 main.py --modulo all "gavgavgav|vagvagvag"

# só a decisão, sem o rastreamento
python3 main.py --sem-rastro "BNLLNESOOSB#gvag|aggg"

# sem argumento, a cadeia é pedida no terminal
python3 main.py
```

O rastreamento do **AP** mostra a cada passo o estado, a posição de leitura, a entrada restante, a pilha (topo à esquerda) e a transição aplicada.
O rastreamento do **ALL** mostra o estado, a posição do cabeçote, a fita inteira (`[ ]` marca o cabeçote, e `<` e `>` são os marcadores de borda) e a transição aplicada.
Um símbolo fora do alfabeto gera uma mensagem de erro e o código de saída 2.

### Cenários de integração

| Entrada | AP | ALL | Decisão |
|---|---|---|---|
| `BNLLNESOOSB#gvag\|aggv` | aceita | aceita | **ACEITA** |
| `BNLLNESOONB#gvag\|aggv` | rejeita: a volta termina em `N`, mas o topo da pilha pede `S` | não executa | **REJEITA no AP** |
| `BNLLNESOOSB#gvag\|aggg` | aceita | rejeita: o reserva tem `g` no lugar de `v` | **REJEITA no ALL** |
| `BNLLNESOOSB#gvxg\|aggv` | (não executa) | (não executa) | **ERRO**: `o 15º símbolo, 'x', não pertence ao alfabeto de entrada {B, N, S, L, O, E, #, \|, g, a, v}` |

## Repetir os testes

```bash
python3 testes.py
```

O script roda os 44 casos de `casos_teste.csv`: 20 do AP, 20 do ALL e 4 de integração, incluindo os casos-limite e o símbolo fora do alfabeto. Para cada caso ele imprime e grava em **`resultados_testes.md`** a entrada, a decisão esperada, a decisão obtida, a regra verificada e a mensagem exibida pelo programa.
Depois faz três checagens extras:
- compara os dois simuladores com um oráculo independente (expressão regular e contagem) em 6000 cadeias aleatórias;
- confere que as folhas de cada árvore de derivação formam a própria cadeia;
- se o Node estiver instalado, confere que o painel web (JS) produz rastreamentos e compilações idênticos aos do Python. Também verifica que `web/automatos.js` está atualizado.
Sai com código 1 se algum teste falhar.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `automato_pilha.py` | AP: alfabeto, tabela δ e simulador com rastreamento |
| `automato_linear.py` | ALL: alfabeto da fita, tabela δ e simulador com fita limitada `< … >` |
| `main.py` | interface de linha de comando e fluxo das duas etapas |
| `compilador.py` | visão de compilador: léxico → sintático (AP) → semântico (ALL) → geração de código |
| `visualizador.py` | exporta as tabelas δ para `web/automatos.js` e abre o painel |
| `web/index.html`, `web/simulador.js`, `web/automatos.js` | painel interativo (pilotar, replay, desafio, visão de compilador), os simuladores em JS e as tabelas δ exportadas |
| `testes.py` | executor dos testes e comparação com o oráculo |
| `casos_teste.csv` | dados de teste: módulo, entrada, decisão esperada e regra |
| `resultados_testes.md` | último resultado gerado por `testes.py` |
| `docs/relatorio.pdf` | relatório técnico (fonte: `docs/relatorio.html`) |
| `docs/slides.pdf` | slides da apresentação (fonte: `docs/slides.html`) |
| `docs/img/` | diagramas de estados (SVG) e captura do visualizador |

Para regenerar os PDFs a partir do HTML (Chrome ou Chromium):

```bash
google-chrome --headless --no-pdf-header-footer --print-to-pdf=docs/relatorio.pdf docs/relatorio.html
google-chrome --headless --no-pdf-header-footer --print-to-pdf=docs/slides.pdf docs/slides.html
```

## Resumo formal

**GLC** G = (V, Σ, P, P), com V = {P, R, G}:

```
P → B R B # G | G
R → N R S | S R N | L R O | O R L | N E S | S E N | L E O | O E L
G → g G | a G | v G | g | a | v
```

**AP** determinístico M = (Q, Σ, Γ, δ, q0, Z, F), com Q = {q0, …, q8} (9 estados), Γ = {N, S, L, O, Z} e F = {q8}. A aceitação é **por estado final**, com a entrada consumida por inteiro. Ao ler um movimento da ida, o AP empilha a volta pendente (o oposto). Na volta, cada símbolo lido precisa ser igual ao topo, que então é desempilhado.

**ALL** determinístico com 12 estados (q0, q1, cg, ca, cv, bg, ba, bv, qr, qv, qac, qrej). A fita tem a forma `< x|y >`: n células graváveis e 2 marcadores fixos. O algoritmo marca com `X` cada evento do principal, leva o evento no estado até o reserva e lá marca o primeiro símbolo igual ainda não marcado. No fim, aceita só se o reserva estiver todo marcado.

A especificação completa (transições, derivação, justificativas, prova de não regularidade e de que a linguagem não é livre de contexto, terminação e análise dos testes) está em `docs/relatorio.pdf`.

## Origem do código e uso de IA

O problema, as gramáticas, os autômatos e os casos de teste foram elaborados para este trabalho e não foram adaptados de exercícios de sala nem do exemplo do enunciado. As referências teóricas estão no relatório.

**Inteligência artificial:** usamos o **Claude Code (Anthropic)** como apoio para:
- propor o problema e a modelagem;
- escrever o código dos simuladores, do painel interativo, da visão de compilador e dos testes;
- redigir o relatório e os slides.

A equipe verificou:
- cada transição dos dois autômatos, comparando o código com as tabelas do relatório;
- os rastreamentos dos três cenários de integração, executados à mão;
- as provas de classificação (lema do bombeamento);
- o resultado de `python3 testes.py`.

## Equipe

| Nome completo | Turma | Contribuição |
|---|---|---|
| _Integrante 1_ | _CC6__ | _…_ |
| _Integrante 2_ | _CC6__ | _…_ |
| _Integrante 3_ | _CC6__ | _…_ |
| _Integrante 4_ | _CC6__ | _…_ |
