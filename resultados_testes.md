# Resultados dos testes

Gerado por `python testes.py` a partir de `casos_teste.csv`.

| # | Módulo | Entrada | Tam. | Esperado | Obtido | Status | Regra verificada | Motivo exibido pelo programa |
|---|---|---|---|---|---|---|---|---|
| 1 | AP | `BNLLNESOOSB#gvag\|aggv` | 21 | ACEITA | ACEITA | OK | ida NLLN desfeita por SOOS: cada movimento é desfeito pelo oposto, do último para o primeiro (LIFO) | aceita: entrada consumida no estado final q8 |
| 2 | AP | `BNLLNESOOSB#gvag\|aggg` | 21 | ACEITA | ACEITA | OK | o AP confere só a estrutura; o conteúdo dos registros é verificado pelo ALL | aceita: entrada consumida no estado final q8 |
| 3 | AP | `BNESB#gavgavgav\|vagvag` | 22 | ACEITA | ACEITA | OK | rota de um movimento; registros de tamanhos diferentes não violam a estrutura | aceita: entrada consumida no estado final q8 |
| 4 | AP | `BOOOELLLB#ggggg\|ggggg` | 21 | ACEITA | ACEITA | OK | três O na ida exigem três L na volta | aceita: entrada consumida no estado final q8 |
| 5 | AP | `BSLNOELSONB#aav\|ava` | 19 | ACEITA | ACEITA | OK | ida SLNO exige volta LSON (inverso de cada movimento, em ordem inversa) | aceita: entrada consumida no estado final q8 |
| 6 | AP | `BNNNNNNESSSSSSB#g\|g` | 19 | ACEITA | ACEITA | OK | N^6 na ida casa com S^6 na volta: a pilha conta os movimentos pendentes | aceita: entrada consumida no estado final q8 |
| 7 | AP | `BLOLOELOLOB#vvav\|vav` | 20 | ACEITA | ACEITA | OK | ida LOLO exige volta LOLO (inverter e trocar pelos opostos) | aceita: entrada consumida no estado final q8 |
| 8 | AP | `BSSLEONNB#aaaa\|aaaa` | 19 | ACEITA | ACEITA | OK | ida SSL exige volta ONN | aceita: entrada consumida no estado final q8 |
| 9 | AP | `BNESB#g\|g` | 9 | ACEITA | ACEITA | OK | caso-limite: menor cadeia aceita (9 símbolos: 1 movimento e 1 evento por registro) | aceita: entrada consumida no estado final q8 |
| 10 | AP | `BNLLNESOONB#gvag\|aggv` | 21 | REJEITA | REJEITA | OK | último movimento da volta (N) não desfaz o primeiro da ida (N exige S) | rejeita: não há δ(q3, N, S); q3 = lendo a volta (desempilha) ou a base B de chegada |
| 11 | AP | `BNLESOB#gvaga\|gvaga` | 19 | REJEITA | REJEITA | OK | volta na mesma ordem da ida (FIFO): a pilha exige desfazer L antes de N | rejeita: não há δ(q3, S, O); q3 = lendo a volta (desempilha) ou a base B de chegada |
| 12 | AP | `BNLLNESOOB#gvag\|gvag` | 20 | REJEITA | REJEITA | OK | volta curta: chega à base com S ainda na pilha | rejeita: não há δ(q3, B, S); q3 = lendo a volta (desempilha) ou a base B de chegada |
| 13 | AP | `BNLLNESOOSSB#gvag\|gvag` | 22 | REJEITA | REJEITA | OK | volta longa: movimento extra quando a pilha só tem Z | rejeita: não há δ(q3, S, Z); q3 = lendo a volta (desempilha) ou a base B de chegada |
| 14 | AP | `NLLNESOOSB#gvag\|gvag` | 20 | REJEITA | REJEITA | OK | o voo não parte da base B | rejeita: não há δ(q0, N, Z); q0 = esperando a base B de partida |
| 15 | AP | `BEB#gvaggvag\|gvaggvag` | 21 | REJEITA | REJEITA | OK | rota vazia: a entrega não pode ser na própria base | rejeita: não há δ(q1, E, Z); q1 = esperando o 1º movimento da ida |
| 16 | AP | `BNLLNESOOSBgvag\|gvag` | 20 | REJEITA | REJEITA | OK | falta o separador # entre a rota e os registros | rejeita: não há δ(q4, g, Z); q4 = esperando o separador # |
| 17 | AP | `BNLLNESOOSB#gvaggva` | 19 | REJEITA | REJEITA | OK | falta o registro reserva (a entrada termina em q6, que não é final) | rejeita: entrada consumida em q6, que não é final (lendo o registro principal ou o separador \|) |
| 18 | AP | `BNLLNESOOSB#gvaggv\|` | 19 | REJEITA | REJEITA | OK | registro reserva vazio (a entrada termina em q7, que não é final) | rejeita: entrada consumida em q7, que não é final (esperando o 1º evento do registro reserva) |
| 19 | AP | `BNLLNESOOSB#gvag\|gvag\|g` | 23 | REJEITA | REJEITA | OK | um terceiro registro (segundo \|) não é permitido | rejeita: não há δ(q8, \|, Z); q8 = lendo o registro reserva (estado final) |
| 20 | AP | *(vazia)* | 0 | REJEITA | REJEITA | OK | caso-limite: entrada vazia termina em q0, que não é final | rejeita: entrada consumida em q0, que não é final (esperando a base B de partida) |
| 21 | ALL | `gavgavgav\|vagvagvag` | 19 | ACEITA | ACEITA | OK | 3 g, 3 a e 3 v nos dois registros | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 22 | ALL | `ggggaaaavv\|vvaaaagggg` | 21 | ACEITA | ACEITA | OK | mesmas quantidades em ordem invertida | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 23 | ALL | `gvagvagvag\|gvagvagvag` | 21 | ACEITA | ACEITA | OK | cópia idêntica também é permutação | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 24 | ALL | `aaaaaaaaa\|aaaaaaaaa` | 19 | ACEITA | ACEITA | OK | um só tipo de evento, 9 de cada lado | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 25 | ALL | `gavvagvvag\|gggaaavvvv` | 21 | ACEITA | ACEITA | OK | 3 g, 3 a e 4 v nos dois registros, em ordens diferentes | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 26 | ALL | `vvvvvgvvvv\|gvvvvvvvvv` | 21 | ACEITA | ACEITA | OK | o único g muda de posição | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 27 | ALL | `agagagagag\|gagagagaga` | 21 | ACEITA | ACEITA | OK | 5 a e 5 g nos dois registros | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 28 | ALL | `vgavgavgav\|aaagggvvvv` | 21 | ACEITA | ACEITA | OK | o reserva agrupa os eventos por tipo | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 29 | ALL | `\|` | 1 | ACEITA | ACEITA | OK | caso-limite: menor cadeia aceita (dois registros vazios) | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 30 | ALL | `gavgavgav\|vagvagvav` | 19 | REJEITA | REJEITA | OK | o reserva trocou um g por um v | rejeita: não há δ(bg, >); bg = procurando um 'g' não marcado no registro reserva |
| 31 | ALL | `gavgavgav\|vagvagva` | 18 | REJEITA | REJEITA | OK | o reserva perdeu um g | rejeita: não há δ(bg, >); bg = procurando um 'g' não marcado no registro reserva |
| 32 | ALL | `gavgavgav\|vagvagvagg` | 20 | REJEITA | REJEITA | OK | o reserva tem um g a mais | rejeita: não há δ(qv, g); qv = principal todo marcado; conferindo se o reserva também está |
| 33 | ALL | `gavgavgavvagvagvag` | 18 | REJEITA | REJEITA | OK | sem o separador \| | rejeita: não há δ(cg, >); cg = levando um 'g' até o separador \| |
| 34 | ALL | `gavgav\|gav\|gavgavgav` | 20 | REJEITA | REJEITA | OK | dois separadores \| | rejeita: não há δ(bg, \|); bg = procurando um 'g' não marcado no registro reserva |
| 35 | ALL | `aaaaaaaaa\|aaaaaaaa` | 18 | REJEITA | REJEITA | OK | o reserva tem um a a menos | rejeita: não há δ(ba, >); ba = procurando um 'a' não marcado no registro reserva |
| 36 | ALL | `vvvvvvvvv\|ggggggggg` | 19 | REJEITA | REJEITA | OK | eventos totalmente diferentes | rejeita: não há δ(bv, >); bv = procurando um 'v' não marcado no registro reserva |
| 37 | ALL | `\|gavgavgavgavgavgav` | 19 | REJEITA | REJEITA | OK | principal vazio e reserva com eventos | rejeita: não há δ(qv, g); qv = principal todo marcado; conferindo se o reserva também está |
| 38 | ALL | `gavgavgavgavgavgav\|` | 19 | REJEITA | REJEITA | OK | principal com eventos e reserva vazio | rejeita: não há δ(bg, >); bg = procurando um 'g' não marcado no registro reserva |
| 39 | ALL | *(vazia)* | 0 | REJEITA | REJEITA | OK | caso-limite: entrada vazia (não há separador) | rejeita: não há δ(q1, >); q1 = procurando o próximo evento não marcado do registro principal |
| 40 | ALL | `gavgavgav\|vagvagvaN` | 19 | ERRO | ERRO | OK | N pertence ao alfabeto do AP, mas não ao do ALL | o 19º símbolo, 'N', não pertence ao alfabeto de entrada {g, a, v, \|} |
| 41 | INTEGRACAO | `BNLLNESOOSB#gvag\|aggv` | 21 | ACEITA | ACEITA | OK | AP aceita a rota; ALL confirma que o reserva é permutação do principal | aceita: todo evento do principal tem um par no reserva e não sobrou evento |
| 42 | INTEGRACAO | `BNLLNESOONB#gvag\|aggv` | 21 | REJEITA_AP | REJEITA_AP | OK | a volta não desfaz a ida; o ALL não é executado | rejeita: não há δ(q3, N, S); q3 = lendo a volta (desempilha) ou a base B de chegada |
| 43 | INTEGRACAO | `BNLLNESOOSB#gvag\|aggg` | 21 | REJEITA_ALL | REJEITA_ALL | OK | estrutura válida, mas o reserva registrou g no lugar de v | rejeita: não há δ(bv, >); bv = procurando um 'v' não marcado no registro reserva |
| 44 | INTEGRACAO | `BNLLNESOOSB#gvxg\|aggv` | 21 | ERRO | ERRO | OK | símbolo x fora do alfabeto de entrada | o 15º símbolo, 'x', não pertence ao alfabeto de entrada {B, N, S, L, O, E, #, \|, g, a, v} |

Comparação com oráculo independente (regex/contagem) em 6000 cadeias aleatórias: 0 divergência(s).

Paridade do painel web (JS × Python: rastreamento passo a passo e visão de compilador) em 2044 cadeias: 0 divergência(s).


**Total: 44 casos fixos, 0 falha(s).**
