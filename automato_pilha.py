"""Etapa 1: autômato de pilha (AP) determinístico que valida a ESTRUTURA do voo.

L_AP = { B w E inv(w) B # x | y  :  w ∈ {N,S,L,O}+,  x, y ∈ {g,a,v}+ }
inv(w) = w lida de trás para frente, com cada direção trocada pela oposta (N↔S, L↔O).

Ao ler um movimento da ida, o AP empilha o movimento de volta que fica pendente.
Na volta, cada símbolo lido precisa ser igual ao topo, que é então desempilhado.
Aceitação por estado final (q8), com a entrada consumida por inteiro.
"""

ALFABETO = "BNSLOE#|gav"
MOVIMENTOS = "NSLO"
EVENTOS = "gav"
OPOSTO = {"N": "S", "S": "N", "L": "O", "O": "L"}
BASE_PILHA = "Z"
INICIAL, FINAIS = "q0", {"q8"}

# δ(estado, símbolo lido, topo) = (novo estado, cadeia que substitui o topo, com o topo à esquerda)
DELTA = {("q0", "B", "Z"): ("q1", "Z")}
for m in MOVIMENTOS:
    DELTA[("q1", m, "Z")] = ("q2", OPOSTO[m] + "Z")  # 1º movimento é obrigatório
    for topo in MOVIMENTOS:
        DELTA[("q2", m, topo)] = ("q2", OPOSTO[m] + topo)
    DELTA[("q2", "E", m)] = ("q3", m)  # ponto de entrega: começa a volta
    DELTA[("q3", m, m)] = ("q3", "")  # volta confere com o topo: desempilha
DELTA[("q3", "B", "Z")] = ("q4", "Z")
DELTA[("q4", "#", "Z")] = ("q5", "Z")
for e in EVENTOS:
    DELTA[("q5", e, "Z")] = ("q6", "Z")
    DELTA[("q6", e, "Z")] = ("q6", "Z")
    DELTA[("q7", e, "Z")] = ("q8", "Z")
    DELTA[("q8", e, "Z")] = ("q8", "Z")
DELTA[("q6", "|", "Z")] = ("q7", "Z")

DESCRICAO = {
    "q0": "esperando a base B de partida",
    "q1": "esperando o 1º movimento da ida",
    "q2": "lendo a ida (empilha a volta pendente) ou o ponto de entrega E",
    "q3": "lendo a volta (desempilha) ou a base B de chegada",
    "q4": "esperando o separador #",
    "q5": "esperando o 1º evento do registro principal",
    "q6": "lendo o registro principal ou o separador |",
    "q7": "esperando o 1º evento do registro reserva",
    "q8": "lendo o registro reserva (estado final)",
}


def simular(cadeia):
    """Executa o AP. Retorna (aceita, rastro, motivo).

    rastro: lista de (estado, posição de leitura, pilha com topo à esquerda, transição aplicada).
    Como o AP é determinístico e toda transição consome um símbolo, para em no máximo len(cadeia) passos.
    """
    estado, pilha, rastro = INICIAL, BASE_PILHA, []
    for pos, simbolo in enumerate(cadeia):
        regra = DELTA.get((estado, simbolo, pilha[0]))
        if regra is None:
            rastro.append((estado, pos, pilha, "sem transição"))
            return False, rastro, (
                f"rejeita: não há δ({estado}, {simbolo}, {pilha[0]}); {estado} = {DESCRICAO[estado]}"
            )
        novo, troca = regra
        rastro.append((estado, pos, pilha, f"δ({estado}, {simbolo}, {pilha[0]}) = ({novo}, {troca or 'ε'})"))
        estado, pilha = novo, troca + pilha[1:]
    rastro.append((estado, len(cadeia), pilha, ""))
    if estado in FINAIS:
        return True, rastro, f"aceita: entrada consumida no estado final {estado}"
    return False, rastro, f"rejeita: entrada consumida em {estado}, que não é final ({DESCRICAO[estado]})"
