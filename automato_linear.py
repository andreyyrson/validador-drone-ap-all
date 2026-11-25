"""Etapa 2: autômato linearmente limitado (ALL) que audita as duas caixas-pretas.

L_ALL = { x | y  :  x, y ∈ {g,a,v}*  e  y é uma permutação de x }
(o registro reserva tem os mesmos eventos do principal, nas mesmas quantidades, em qualquer ordem)

Fita: < x|y >, com n células graváveis e os marcadores fixos < e >.
Algoritmo: marca (X) o próximo evento do principal, leva-o "na memória do estado"
até o reserva, marca lá o primeiro igual ainda não marcado e volta ao <.
Quando o principal acaba, aceita só se o reserva estiver todo marcado.
"""

ALFABETO = "gav|"
EVENTOS = "gav"
ESQ, DIR, MARCA = "<", ">", "X"
INICIAL, ACEITA, REJEITA = "q0", "qac", "qrej"

# δ(estado, símbolo lido) = (novo estado, símbolo escrito, movimento: +1 direita, -1 esquerda, 0 parado)
DELTA = {
    ("q0", ESQ): ("q1", ESQ, +1),
    ("q1", MARCA): ("q1", MARCA, +1),
    ("q1", "|"): ("qv", "|", +1),  # principal acabou: conferir o reserva
    ("qv", MARCA): ("qv", MARCA, +1),
    ("qv", DIR): (ACEITA, DIR, 0),
    ("qr", ESQ): ("q1", ESQ, +1),
}
for e in EVENTOS:
    leva, busca = "c" + e, "b" + e  # c: carregando e pelo principal; b: buscando e no reserva
    DELTA[("q1", e)] = (leva, MARCA, +1)
    DELTA[(leva, "|")] = (busca, "|", +1)
    DELTA[(busca, MARCA)] = (busca, MARCA, +1)
    DELTA[(busca, e)] = ("qr", MARCA, -1)
    for s in EVENTOS:
        DELTA[(leva, s)] = (leva, s, +1)
        if s != e:
            DELTA[(busca, s)] = (busca, s, +1)
for s in EVENTOS + "|" + MARCA:
    DELTA[("qr", s)] = ("qr", s, -1)

DESCRICAO = {
    "q0": "início, cabeçote no marcador <",
    "q1": "procurando o próximo evento não marcado do registro principal",
    "qr": "voltando ao marcador <",
    "qv": "principal todo marcado; conferindo se o reserva também está",
    **{"c" + e: f"levando um '{e}' até o separador |" for e in EVENTOS},
    **{"b" + e: f"procurando um '{e}' não marcado no registro reserva" for e in EVENTOS},
}


def simular(cadeia):
    """Executa o ALL. Retorna (aceita, rastro, motivo).

    rastro: lista de (estado, posição do cabeçote, conteúdo da fita, transição aplicada).
    Termina sempre: cada volta q1→c→b→qr marca um evento do principal, e cada varredura
    percorre no máximo n+2 células, então são O(n²) passos.
    """
    fita = [ESQ, *cadeia, DIR]
    estado, cab, rastro = INICIAL, 0, []
    while estado not in (ACEITA, REJEITA):
        lido = fita[cab]
        regra = DELTA.get((estado, lido))
        if regra is None:
            rastro.append((estado, cab, "".join(fita), f"sem transição → {REJEITA}"))
            motivo = f"rejeita: não há δ({estado}, {lido}); {estado} = {DESCRICAO[estado]}"
            estado = REJEITA
            break
        novo, escrito, mov = regra
        if lido in (ESQ, DIR) and escrito != lido or not 0 <= cab + mov < len(fita):
            raise RuntimeError(f"transição {regra} violaria o limite da fita")
        rastro.append((estado, cab, "".join(fita), f"δ({estado}, {lido}) = ({novo}, {escrito}, {'EPD'[mov + 1]})"))
        fita[cab], cab, estado = escrito, cab + mov, novo
    if estado == ACEITA:
        motivo = "aceita: todo evento do principal tem um par no reserva e não sobrou evento"
    rastro.append((estado, cab, "".join(fita), ""))
    return estado == ACEITA, rastro, motivo
