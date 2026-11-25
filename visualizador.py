"""Painel interativo: exporta as tabelas δ do Python para web/automatos.js e abre web/index.html.

O painel roda sozinho no navegador (sem servidor), então também funciona com duplo clique
no index.html ou publicado no GitHub Pages. Ele executa estas mesmas tabelas com web/simulador.js,
e testes.py confere que o JS produz rastreamentos idênticos aos do Python.
Uso: python visualizador.py
"""
import json
import webbrowser
from pathlib import Path

import automato_linear
import automato_pilha

PASTA_WEB = Path(__file__).resolve().parent / "web"
ARQUIVO_JS = PASTA_WEB / "automatos.js"


def gerar_js():
    ap, al = automato_pilha, automato_linear
    dados = {
        "ap": {
            "alfabeto": ap.ALFABETO, "inicial": ap.INICIAL, "finais": sorted(ap.FINAIS), "base": ap.BASE_PILHA,
            "delta": [[q, a, t, p, g] for (q, a, t), (p, g) in ap.DELTA.items()], "descricao": ap.DESCRICAO,
        },
        "all": {
            "alfabeto": al.ALFABETO, "inicial": al.INICIAL, "aceita": al.ACEITA, "rejeita": al.REJEITA,
            "esq": al.ESQ, "dir": al.DIR,
            "delta": [[q, s, p, w, m] for (q, s), (p, w, m) in al.DELTA.items()], "descricao": al.DESCRICAO,
        },
    }
    return (
        "// Gerado por visualizador.py a partir de automato_pilha.py e automato_linear.py. Não edite à mão.\n"
        f"const AUTOMATOS = {json.dumps(dados, ensure_ascii=False)};\n"
        'if (typeof module !== "undefined") module.exports = AUTOMATOS;\n'
    )


if __name__ == "__main__":
    ARQUIVO_JS.write_text(gerar_js(), encoding="utf-8")
    pagina = PASTA_WEB / "index.html"
    print(f"Painel: {pagina}")
    webbrowser.open(pagina.as_uri())
