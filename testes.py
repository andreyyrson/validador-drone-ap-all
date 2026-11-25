"""Testes: executa casos_teste.csv, mostra a tabela e grava resultados_testes.md.

Além dos casos fixos, compara os dois simuladores com um oráculo direto
(expressão regular + contagem) em milhares de cadeias aleatórias, para pegar
erros de modelagem que os casos escritos à mão não cobrem. Se o Node estiver instalado,
confere também que o painel web (web/simulador.js) gera rastreamentos idênticos aos do Python.
Uso: python testes.py   (sai com código 1 se algum teste falhar)
"""
import csv
import json
import random
import re
import shutil
import subprocess
import sys

import automato_linear
import automato_pilha
import visualizador
from compilador import compilar
from main import erro_alfabeto, validar

MODULOS = {"AP": automato_pilha, "ALL": automato_linear}


def decidir(modulo, cadeia):
    if modulo == "INTEGRACAO":
        decisao, motivo, _, _ = validar(cadeia)
        return decisao, motivo
    automato = MODULOS[modulo]
    erro = erro_alfabeto(cadeia, automato.ALFABETO)
    if erro:
        return "ERRO", erro
    aceita, _, motivo = automato.simular(cadeia)
    return ("ACEITA" if aceita else "REJEITA"), motivo


def oraculo_ap(cadeia):
    m = re.fullmatch(r"B([NSLO]+)E([NSLO]+)B#[gav]+\|[gav]+", cadeia)
    return bool(m) and m[2] == m[1][::-1].translate(str.maketrans("NSLO", "SNOL"))


def oraculo_all(cadeia):
    partes = cadeia.split("|")
    return len(partes) == 2 and sorted(partes[0]) == sorted(partes[1])


def gerar_ap(rng):
    ida = "".join(rng.choices("NSLO", k=rng.randint(1, 6)))
    volta = ida[::-1].translate(str.maketrans("NSLO", "SNOL"))
    x = "".join(rng.choices("gav", k=rng.randint(1, 5)))
    y = "".join(rng.choices("gav", k=rng.randint(1, 5)))
    cadeia = f"B{ida}E{volta}B#{x}|{y}"
    if rng.random() < 0.5:  # perturba um símbolo para gerar quase-acertos
        i = rng.randrange(len(cadeia))
        cadeia = cadeia[:i] + rng.choice(automato_pilha.ALFABETO) + cadeia[i + 1:]
    return cadeia


def gerar_all(rng):
    x = "".join(rng.choices("gav", k=rng.randint(0, 7)))
    y = "".join(rng.sample(x, len(x)))
    cadeia = f"{x}|{y}"
    if rng.random() < 0.5:
        i = rng.randrange(len(cadeia))
        cadeia = cadeia[:i] + rng.choice(automato_linear.ALFABETO) + cadeia[i + 1:]
    return cadeia


def folhas(no):
    return no if isinstance(no, str) else "".join(folhas(f) for f in no[1])


def cruzar_com_oraculo(rng, n=3000):
    divergencias = []
    for automato, gerar, oraculo in (
        (automato_pilha, gerar_ap, oraculo_ap),
        (automato_linear, gerar_all, oraculo_all),
    ):
        for _ in range(n):
            cadeia = gerar(rng)
            if automato.simular(cadeia)[0] != oraculo(cadeia):
                divergencias.append((automato.__name__, cadeia))
            arvore = compilar(cadeia)["arvore"] if automato is automato_pilha else None
            if arvore and folhas(arvore) != cadeia:  # a árvore de derivação precisa gerar a cadeia lida
                divergencias.append(("compilador.arvore", cadeia))
    return divergencias


def paridade_js(casos):
    """Roda web/simulador.js no Node; devolve as cadeias em que o JS diverge do Python (None se não há Node)."""
    if not shutil.which("node"):
        return None
    script = """
      const s = require('./web/simulador.js'); let d = '';
      const rastro = (r, k) => r && r.passos.map((p) => [p.estado, p[k], p.pilha ?? p.fita, p.transicao]);
      process.stdin.on('data', (c) => (d += c)).on('end', () => console.log(JSON.stringify(JSON.parse(d).map(([tipo, c]) => {
        if (tipo === 'ALL') { const r = s.simularALL(c); return [r.aceita, r.motivo, rastro(r, 'cab')]; }
        const r = s.validar(c); return [r.decisao, r.motivo, rastro(r.ap, 'pos'), rastro(r.all, 'cab'), s.compilar(c)];
      }))));"""
    saida = subprocess.run(["node", "-e", script], input=json.dumps(casos), capture_output=True,
                           text=True, encoding="utf-8", check=True).stdout
    divergentes = []
    for (tipo, cadeia), js in zip(casos, json.loads(saida)):
        if tipo == "ALL":
            aceita, rastro, motivo = automato_linear.simular(cadeia)
            py = [aceita, motivo, [list(p) for p in rastro]]
        else:
            decisao, motivo, r_ap, r_all = validar(cadeia)
            py = [decisao, motivo, r_ap and [list(p) for p in r_ap[1]], r_all and [list(p) for p in r_all[1]],
                  compilar(cadeia)]
        if py != js:
            divergentes.append(cadeia)
    return divergentes


def celula(texto):
    return texto.replace("|", "\\|")  # no GitHub, | dentro da tabela precisa de escape


def main():
    with open("casos_teste.csv", encoding="utf-8") as f:
        casos = list(csv.DictReader(f))

    linhas, falhas = [], 0
    for n, caso in enumerate(casos, 1):
        obtido, motivo = decidir(caso["modulo"], caso["entrada"])
        ok = obtido == caso["esperado"]
        falhas += not ok
        entrada = f"`{celula(caso['entrada'])}`" if caso["entrada"] else "*(vazia)*"
        linhas.append(
            f"| {n} | {caso['modulo']} | {entrada} | {len(caso['entrada'])} | {caso['esperado']} "
            f"| {obtido} | {'OK' if ok else '**FALHOU**'} | {celula(caso['regra'])} | {celula(motivo)} |"
        )

    rng = random.Random(2026)
    divergencias = cruzar_com_oraculo(rng)
    falhas += len(divergencias)

    with open(visualizador.ARQUIVO_JS, encoding="utf-8") as f:
        js_atualizado = f.read() == visualizador.gerar_js()
    falhas += not js_atualizado
    casos_js = [("ALL" if c["modulo"] == "ALL" else "FLUXO", c["entrada"]) for c in casos]
    casos_js += [("FLUXO", gerar_ap(rng)) for _ in range(1000)] + [("ALL", gerar_all(rng)) for _ in range(1000)]
    divergentes_js = paridade_js(casos_js)
    falhas += len(divergentes_js or [])
    if divergentes_js is None:
        linha_js = "Paridade do painel web (JS × Python): pulada, Node não encontrado."
    else:
        linha_js = (f"Paridade do painel web (JS × Python: rastreamento passo a passo e visão de compilador) em {len(casos_js)} cadeias: "
                    f"{len(divergentes_js)} divergência(s).")

    relatorio = [
        "# Resultados dos testes",
        "",
        "Gerado por `python testes.py` a partir de `casos_teste.csv`.",
        "",
        "| # | Módulo | Entrada | Tam. | Esperado | Obtido | Status | Regra verificada | Motivo exibido pelo programa |",
        "|---|---|---|---|---|---|---|---|---|",
        *linhas,
        "",
        f"Comparação com oráculo independente (regex/contagem) em 6000 cadeias aleatórias: "
        f"{len(divergencias)} divergência(s).",
        *(f"- {modulo}: `{cadeia}`" for modulo, cadeia in divergencias),
        "",
        linha_js,
        *(f"- `{cadeia}`" for cadeia in (divergentes_js or [])),
        "" if js_atualizado else "**web/automatos.js desatualizado: rode `python visualizador.py`.**",
        "",
        f"**Total: {len(casos)} casos fixos, {falhas} falha(s).**",
    ]
    texto = "\n".join(relatorio) + "\n"
    with open("resultados_testes.md", "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
