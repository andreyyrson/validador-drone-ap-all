// Simuladores do AP e do ALL para o painel. Executam as tabelas δ exportadas do Python (automatos.js),
// com o mesmo laço e as mesmas mensagens de automato_pilha.py e automato_linear.py.
// testes.py roda este arquivo no Node e confere que decisões e rastreamentos são idênticos aos do Python.
(function (raiz) {
  const A = typeof AUTOMATOS !== "undefined" ? AUTOMATOS : require("./automatos.js");
  const chave = (...partes) => partes.join("\t"); // tab não pertence a nenhum alfabeto
  const deltaAP = new Map(A.ap.delta.map(([q, a, t, p, g]) => [chave(q, a, t), [p, g]]));
  const deltaALL = new Map(A.all.delta.map(([q, s, p, w, m]) => [chave(q, s), [p, w, m]]));

  function simularAP(cadeia) {
    const simbolos = Array.from(cadeia), d = A.ap.descricao, passos = [];
    let estado = A.ap.inicial, pilha = A.ap.base;
    for (let pos = 0; pos < simbolos.length; pos++) {
      const s = simbolos[pos], regra = deltaAP.get(chave(estado, s, pilha[0]));
      if (!regra) {
        passos.push({ estado, pos, pilha, transicao: "sem transição" });
        return { aceita: false, passos, motivo: `rejeita: não há δ(${estado}, ${s}, ${pilha[0]}); ${estado} = ${d[estado]}` };
      }
      const [novo, troca] = regra;
      passos.push({ estado, pos, pilha, transicao: `δ(${estado}, ${s}, ${pilha[0]}) = (${novo}, ${troca || "ε"})` });
      estado = novo;
      pilha = troca + pilha.slice(1);
    }
    passos.push({ estado, pos: simbolos.length, pilha, transicao: "" });
    return A.ap.finais.includes(estado)
      ? { aceita: true, passos, motivo: `aceita: entrada consumida no estado final ${estado}` }
      : { aceita: false, passos, motivo: `rejeita: entrada consumida em ${estado}, que não é final (${d[estado]})` };
  }

  function simularALL(cadeia) {
    const L = A.all, fita = [L.esq, ...Array.from(cadeia), L.dir], passos = [];
    let estado = L.inicial, cab = 0, motivo = "";
    while (estado !== L.aceita && estado !== L.rejeita) {
      const lido = fita[cab], regra = deltaALL.get(chave(estado, lido));
      if (!regra) {
        passos.push({ estado, cab, fita: fita.join(""), transicao: `sem transição → ${L.rejeita}` });
        motivo = `rejeita: não há δ(${estado}, ${lido}); ${estado} = ${L.descricao[estado]}`;
        estado = L.rejeita;
        break;
      }
      const [novo, escrito, mov] = regra;
      if (((lido === L.esq || lido === L.dir) && escrito !== lido) || cab + mov < 0 || cab + mov >= fita.length)
        throw new Error(`transição ${regra} violaria o limite da fita`);
      passos.push({ estado, cab, fita: fita.join(""), transicao: `δ(${estado}, ${lido}) = (${novo}, ${escrito}, ${"EPD"[mov + 1]})` });
      fita[cab] = escrito;
      cab += mov;
      estado = novo;
    }
    if (estado === L.aceita) motivo = "aceita: todo evento do principal tem um par no reserva e não sobrou evento";
    passos.push({ estado, cab, fita: fita.join(""), transicao: "" });
    return { aceita: estado === L.aceita, passos, motivo };
  }

  function erroAlfabeto(cadeia, alfabeto) {
    const simbolos = Array.from(cadeia);
    const i = simbolos.findIndex((s) => !alfabeto.includes(s));
    return i < 0 ? null
      : `o ${i + 1}º símbolo, '${simbolos[i]}', não pertence ao alfabeto de entrada {${Array.from(alfabeto).join(", ")}}`;
  }

  function validar(cadeia) {
    const erro = erroAlfabeto(cadeia, A.ap.alfabeto);
    if (erro) return { cadeia, decisao: "ERRO", motivo: erro, ap: null, all: null };
    const ap = simularAP(cadeia);
    if (!ap.aceita) return { cadeia, decisao: "REJEITA_AP", motivo: ap.motivo, ap, all: null };
    const all = simularALL(cadeia.slice(cadeia.indexOf("#") + 1)); // o AP garante exatamente um '#'
    return { cadeia, decisao: all.aceita ? "ACEITA" : "REJEITA_ALL", motivo: all.motivo, ap, all };
  }

  // Missão aleatória para o modo desafio: correta ou com um defeito típico (a decisão vem de validar()).
  function sortearMissao(rnd = Math.random) {
    const pega = (s) => s[Math.floor(rnd() * s.length)];
    const seq = (alf, min, max) => Array.from({ length: min + Math.floor(rnd() * (max - min + 1)) }, () => pega(alf)).join("");
    const troca = (s, i, por) => s.slice(0, i) + por + s.slice(i + 1);
    const OP = { N: "S", S: "N", L: "O", O: "L" };
    const ida = seq("NSLO", 2, 4), x = seq("gav", 2, 4);
    let volta = Array.from(ida).reverse().map((c) => OP[c]).join("");
    const y = Array.from(x);
    for (let i = y.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [y[i], y[j]] = [y[j], y[i]]; }
    let reserva = y.join("");
    const defeito = pega(["nenhum", "nenhum", "volta", "fifo", "curta", "evento", "sobra"]);
    if (defeito === "volta") { const i = Math.floor(rnd() * volta.length); volta = troca(volta, i, pega("NSLO".replace(volta[i], ""))); }
    if (defeito === "fifo") volta = Array.from(ida).map((c) => OP[c]).join("");
    if (defeito === "curta") volta = volta.slice(0, -1);
    if (defeito === "evento") { const i = Math.floor(rnd() * reserva.length); reserva = troca(reserva, i, pega("gav".replace(reserva[i], ""))); }
    if (defeito === "sobra") reserva += pega("gav");
    return `B${ida}E${volta}B#${x}|${reserva}`;
  }

  // ---------- visão de compilador (espelha compilador.py) ----------
  const TOKENS = { B: "BASE", E: "ENTREGA", "#": "FIM_VOO", "|": "SEP", N: "MOVE(N)", S: "MOVE(S)", L: "MOVE(L)", O: "MOVE(O)",
    g: "EVENTO(gps)", a: "EVENTO(bateria)", v: "EVENTO(vento)" };
  const EVENTO = { g: "gps", a: "bateria", v: "vento" };
  const OPOSTO = { N: "S", S: "N", L: "O", O: "L" };

  function arvore(cadeia) { // nó = [não terminal, filhos]; folha = terminal
    const rota = (ida) => ["R", [ida[0], ida.length > 1 ? rota(ida.slice(1)) : "E", OPOSTO[ida[0]]]];
    const registro = (ev) => ["G", [ev[0], ...(ev.length > 1 ? [registro(ev.slice(1))] : [])]];
    const [x, y] = cadeia.slice(cadeia.indexOf("#") + 1).split("|");
    return ["P", ["B", rota(cadeia.slice(1, cadeia.indexOf("E"))), "B", "#", registro(x), "|", registro(y)]];
  }

  function gerarCodigo(cadeia) {
    const e = cadeia.indexOf("E"), h = cadeia.indexOf("#"), principal = cadeia.slice(h + 1, cadeia.indexOf("|"));
    const conta = (c) => principal.split(c).length - 1;
    const bruto = ["DECOLA", ...Array.from(cadeia.slice(1, e), (m) => `MOVE ${m}`), "ENTREGA",
      ...Array.from(cadeia.slice(e + 1, h - 1), (m) => `MOVE ${m}`), "POUSA",
      "AUDITA " + Array.from("gav").filter((c) => principal.includes(c)).map((c) => `${EVENTO[c]}:${conta(c)}`).join(" ")];
    const otimizado = []; // peephole: MOVEs iguais e consecutivos viram uma instrução com repetição
    for (const ins of bruto) {
      if (otimizado.length && ins.startsWith("MOVE") && otimizado.at(-1)[0] === ins) otimizado.at(-1)[1]++;
      else otimizado.push([ins, 1]);
    }
    return [bruto.length, otimizado.map(([ins, n], i) => `${String(i).padStart(2, "0")}  ${ins}${n > 1 ? `, ${n}` : ""}`)];
  }

  function compilar(cadeia) {
    const v = validar(cadeia);
    const r = { decisao: v.decisao, tokens: null, erro: null, arvore: null, codigo: null, instrucoes_antes: null };
    if (v.decisao === "ERRO") { r.erro = `erro léxico: ${v.motivo}`; return r; }
    r.tokens = Array.from(cadeia, (s) => TOKENS[s]);
    if (v.decisao === "REJEITA_AP") { r.erro = `erro sintático (AP): ${v.motivo}`; return r; }
    r.arvore = arvore(cadeia);
    if (v.decisao === "REJEITA_ALL") { r.erro = `erro semântico (ALL): ${v.motivo}`; return r; }
    [r.instrucoes_antes, r.codigo] = gerarCodigo(cadeia);
    return r;
  }

  const api = { simularAP, simularALL, erroAlfabeto, validar, sortearMissao, compilar, AUTOMATOS: A };
  if (typeof module !== "undefined") module.exports = api;
  else Object.assign(raiz, api);
})(this);
