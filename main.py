"""Validador de voos de drone de entrega em duas etapas.

Etapa 1 (AP): a rota de volta desfaz a ida e a cadeia tem o formato B w E inv(w) B # x | y.
Etapa 2 (ALL): só roda se o AP aceitar; confere se o registro reserva y é permutação do principal x.

Uso:
  python main.py "BNLLNESOOSB#gvag|aggv"        fluxo completo com rastreamento
  python main.py --modulo ap  "<cadeia>"        só o autômato de pilha
  python main.py --modulo all "gvag|aggv"       só o autômato linearmente limitado
  python main.py --demo                         os três cenários de integração
  python main.py --sem-rastro "<cadeia>"        só a decisão
"""
import argparse
import sys

import automato_linear
import automato_pilha

CENARIOS_DEMO = [
    ("AP aceita e ALL aceita", "BNLLNESOOSB#gvag|aggv"),
    ("AP rejeita (ALL não executa)", "BNLLNESOONB#gvag|aggv"),
    ("AP aceita e ALL rejeita", "BNLLNESOOSB#gvag|aggg"),
]


def erro_alfabeto(cadeia, alfabeto):
    for i, simbolo in enumerate(cadeia, 1):
        if simbolo not in alfabeto:
            return (
                f"o {i}º símbolo, '{simbolo}', não pertence ao alfabeto de entrada "
                f"{{{', '.join(alfabeto)}}}"
            )
    return None


def validar(cadeia):
    """Fluxo completo. Retorna (decisão, motivo, resultado do AP, resultado do ALL ou None)."""
    erro = erro_alfabeto(cadeia, automato_pilha.ALFABETO)
    if erro:
        return "ERRO", erro, None, None
    r_ap = automato_pilha.simular(cadeia)
    if not r_ap[0]:
        return "REJEITA_AP", r_ap[2], r_ap, None
    r_all = automato_linear.simular(cadeia.split("#", 1)[1])  # o AP garante exatamente um '#'
    return ("ACEITA" if r_all[0] else "REJEITA_ALL"), r_all[2], r_ap, r_all


def mostrar_ap(cadeia, resultado):
    _, rastro, motivo = resultado
    largura = max(len(cadeia), 16)
    print(f"\n[AP] rastreamento de '{cadeia}'")
    print(f"{'passo':>5}  {'estado':<6} {'pos':>3}  {'entrada restante':<{largura}}  {'pilha (topo→base)':<18} transição")
    for passo, (estado, pos, pilha, transicao) in enumerate(rastro):
        print(f"{passo:>5}  {estado:<6} {pos:>3}  {cadeia[pos:] or 'ε':<{largura}}  {pilha:<18} {transicao}")
    print(f"[AP] {motivo}")


def mostrar_all(cadeia, resultado):
    _, rastro, motivo = resultado
    print(f"\n[ALL] rastreamento de '{cadeia}' (fita com {len(cadeia)} células graváveis + marcadores < e >)")
    print(f"{'passo':>5}  {'estado':<6} {'cab':>3}  fita ([ ] = cabeçote){'':<{max(0, 3 * len(cadeia) - 15)}}  transição")
    for passo, (estado, cab, fita, transicao) in enumerate(rastro):
        celulas = "".join(f"[{c}]" if i == cab else f" {c} " for i, c in enumerate(fita))
        print(f"{passo:>5}  {estado:<6} {cab:>3}  {celulas}  {transicao}")
    print(f"[ALL] {motivo}")


def executar(cadeia, modulo=None, rastro=True):
    """Roda um módulo ou o fluxo completo, imprime o resultado e devolve a decisão."""
    if modulo:
        automato = automato_pilha if modulo == "ap" else automato_linear
        erro = erro_alfabeto(cadeia, automato.ALFABETO)
        if erro:
            print(f"ERRO: {erro}")
            return "ERRO"
        resultado = automato.simular(cadeia)
        if rastro:
            (mostrar_ap if modulo == "ap" else mostrar_all)(cadeia, resultado)
        decisao = "ACEITA" if resultado[0] else "REJEITA"
        print(f"\nDecisão do {modulo.upper()}: {decisao} ({resultado[2]})")
        return decisao

    decisao, motivo, r_ap, r_all = validar(cadeia)
    if decisao == "ERRO":
        print(f"ERRO: {motivo}")
        return decisao
    if rastro:
        mostrar_ap(cadeia, r_ap)
        if r_all:
            mostrar_all(cadeia.split("#", 1)[1], r_all)
    print(f"\nAP: {'ACEITA' if r_ap[0] else 'REJEITA'}")
    print(f"ALL: {('ACEITA' if r_all[0] else 'REJEITA') if r_all else 'não executado (o AP rejeitou)'}")
    print(f"Decisão final: {decisao} ({motivo})")
    return decisao


def main():
    parser = argparse.ArgumentParser(description="Validador de voos de drone: AP (rota) + ALL (caixas-pretas).")
    parser.add_argument("entrada", nargs="?", help="cadeia a validar (se omitida, é pedida no terminal)")
    parser.add_argument("--modulo", choices=["ap", "all"], help="executa só um dos reconhecedores")
    parser.add_argument("--demo", action="store_true", help="executa os três cenários de integração")
    parser.add_argument("--sem-rastro", action="store_true", help="mostra só a decisão")
    args = parser.parse_args()

    if args.demo:
        for titulo, cadeia in CENARIOS_DEMO:
            print(f"\n{'=' * 80}\nCenário: {titulo}\nEntrada: {cadeia} ({len(cadeia)} símbolos)\n{'=' * 80}")
            executar(cadeia, rastro=not args.sem_rastro)
        return

    cadeia = args.entrada if args.entrada is not None else input("Cadeia: ").strip()
    decisao = executar(cadeia, args.modulo, rastro=not args.sem_rastro)
    sys.exit({"ERRO": 2}.get(decisao, 0))


if __name__ == "__main__":
    main()
