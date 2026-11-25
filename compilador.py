"""Visão de compilador: o validador como front-end da "linguagem de plano de voo".

Cada fase usa um nível da hierarquia de Chomsky:
  1. léxica: cada símbolo vira um token; Σ* é regular (tipo 3) e um símbolo estranho é erro léxico;
  2. sintática: o AP reconhece a GLC (tipo 2) e a árvore de derivação é montada;
  3. semântica: o ALL confere a regra sensível ao contexto (tipo 1). Compiladores fazem o mesmo com
     "declarar antes de usar" e "número de parâmetros", que não são livres de contexto (Aho et al.);
  4. geração de código: instruções para o drone, com otimização peephole.
Uso: python compilador.py "BNLLNESOOSB#gvag|aggv"
"""
import sys

from automato_pilha import OPOSTO
from main import validar

TOKENS = {"B": "BASE", "E": "ENTREGA", "#": "FIM_VOO", "|": "SEP", **{m: f"MOVE({m})" for m in "NSLO"},
          "g": "EVENTO(gps)", "a": "EVENTO(bateria)", "v": "EVENTO(vento)"}
EVENTO = {"g": "gps", "a": "bateria", "v": "vento"}


def arvore(cadeia):
    """Árvore de derivação de uma cadeia aceita pelo AP: nó = [não terminal, filhos]; folha = terminal."""
    def rota(ida):  # R → x R opp(x) | x E opp(x)
        return ["R", [ida[0], rota(ida[1:]) if len(ida) > 1 else "E", OPOSTO[ida[0]]]]

    def registro(eventos):  # G → e G | e
        return ["G", [eventos[0], *([registro(eventos[1:])] if len(eventos) > 1 else [])]]

    x, y = cadeia[cadeia.index("#") + 1:].split("|")
    return ["P", ["B", rota(cadeia[1:cadeia.index("E")]), "B", "#", registro(x), "|", registro(y)]]


def gerar_codigo(cadeia):
    """Traduz uma missão válida em instruções; devolve (nº de instruções antes da otimização, código otimizado)."""
    e, h = cadeia.index("E"), cadeia.index("#")
    principal = cadeia[h + 1:cadeia.index("|")]
    bruto = ["DECOLA", *(f"MOVE {m}" for m in cadeia[1:e]), "ENTREGA", *(f"MOVE {m}" for m in cadeia[e + 1:h - 1]),
             "POUSA", "AUDITA " + " ".join(f"{EVENTO[c]}:{principal.count(c)}" for c in "gav" if c in principal)]
    otimizado = []  # peephole: MOVEs iguais e consecutivos viram uma instrução com repetição
    for instrucao in bruto:
        if otimizado and instrucao.startswith("MOVE") and otimizado[-1][0] == instrucao:
            otimizado[-1][1] += 1
        else:
            otimizado.append([instrucao, 1])
    return len(bruto), [f"{i:02d}  {ins}" + (f", {n}" if n > 1 else "") for i, (ins, n) in enumerate(otimizado)]


def compilar(cadeia):
    decisao, motivo, r_ap, r_all = validar(cadeia)
    resultado = {"decisao": decisao, "tokens": None, "erro": None, "arvore": None, "codigo": None, "instrucoes_antes": None}
    if decisao == "ERRO":
        resultado["erro"] = f"erro léxico: {motivo}"
        return resultado
    resultado["tokens"] = [TOKENS[s] for s in cadeia]
    if decisao == "REJEITA_AP":
        resultado["erro"] = f"erro sintático (AP): {motivo}"
        return resultado
    resultado["arvore"] = arvore(cadeia)
    if decisao == "REJEITA_ALL":
        resultado["erro"] = f"erro semântico (ALL): {motivo}"
        return resultado
    resultado["instrucoes_antes"], resultado["codigo"] = gerar_codigo(cadeia)
    return resultado


def desenhar(no, prefixo="", ultimo=True, raiz=True):
    rotulo = no if isinstance(no, str) else no[0]
    linhas = [rotulo if raiz else f"{prefixo}{'└─ ' if ultimo else '├─ '}{rotulo}"]
    if not isinstance(no, str):
        filhos, recuo = no[1], "" if raiz else prefixo + ("   " if ultimo else "│  ")
        for i, filho in enumerate(filhos):
            linhas += desenhar(filho, recuo, i == len(filhos) - 1, False)
    return linhas


if __name__ == "__main__":
    cadeia = sys.argv[1] if len(sys.argv) > 1 else input("Missão: ").strip()
    r = compilar(cadeia)
    print(f"1. Léxica (regular): {' '.join(r['tokens']) if r['tokens'] else '—'}")
    if r["arvore"]:
        print("2. Sintática (AP, livre de contexto): ok. Árvore de derivação:")
        print("\n".join("     " + linha for linha in desenhar(r["arvore"])))
    if r["codigo"]:
        print("3. Semântica (ALL, sensível ao contexto): ok, as caixas-pretas conferem")
        print(f"4. Código gerado ({r['instrucoes_antes']} → {len(r['codigo'])} instruções após a otimização peephole):")
        print("\n".join("     " + linha for linha in r["codigo"]))
    if r["erro"]:
        print(f"\nCompilação interrompida: {r['erro']}")
    sys.exit(0 if r["decisao"] == "ACEITA" else 1)
