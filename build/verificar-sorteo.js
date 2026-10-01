// Verifica que el sorteo de index.html sea justo con los datos reales.
// Uso: node build/verificar-sorteo.js [sorteos] [id de la lotería, por defecto moto]
// Extrae del index.html las funciones reales del sorteo (randInt, indexAt) y repite el mismo cálculo
// que hace spin(): sortea un ticket con crypto.getRandomValues, calcula dónde cae la flecha y comprueba
// que (1) la flecha siempre quede en la casilla de quien se sorteó y (2) cada persona gane en proporción
// a sus tickets (prueba chi-cuadrado).
const fs = require("fs"), path = require("path");
const R = path.join(__dirname, "..");
global.window = {};
require(path.join(R, "data", "participantes.js"));
const html = fs.readFileSync(path.join(R, "index.html"), "utf8");
const grab = name => {
  const i = html.indexOf(`  function ${name}(`);
  const m = /\r?\n  \}\r?\n/g; m.lastIndex = i; const e = m.exec(html);
  if (i < 0 || !e) throw new Error(`No encontré ${name} en index.html`);
  return html.slice(i, e.index + e[0].length);
};
let current = [], starts = [0];
const { randInt, indexAt } = new Function("getCurrent", "getStarts",
  grab("randInt") + grab("indexAt").replace(/\bcurrent\b/g, "getCurrent()").replace(/\bstarts\b/g, "getStarts()") +
  "return { randInt, indexAt };")(() => current, () => starts);

const LOT = window.LOTERIAS.find(l => l.id === (process.argv[3] || "moto"));
if (!LOT || !LOT.participantes.length) { console.log("Esa lotería no existe o no tiene participantes."); process.exit(1); }
const EXCLUIDAS = new Set(LOT.excluidas || ["Auteco", "La Causa", "Galilei"]);
const MINIMO = Math.max(1, LOT.minimo || 1);
current = LOT.participantes.filter(p => p.t >= MINIMO && !EXCLUIDAS.has(p.c || "Sin empresa"));
const tau = Math.PI * 2, total = current.reduce((a, p) => a + p.t, 0);
let acc = 0; starts = [0]; current.forEach(p => { acc += p.t; starts.push(acc / total * tau); }); starts[starts.length - 1] = tau;

const N = +process.argv[2] || 3000000;
const gana = new Array(current.length).fill(0);
let fuera = 0, rot = 0;
for (let i = 0; i < N; i++) {
  let ticket = randInt(total), k = 0;
  while (ticket >= current[k].t) { ticket -= current[k].t; k++; }
  const w = starts[k + 1] - starts[k], off = starts[k] + w * (0.2 + 0.6 * randInt(1000000) / 1000000);
  const cur = ((-rot % tau) + tau) % tau, delta = ((cur - off) % tau + tau) % tau;
  rot = rot + delta + (10 + randInt(3)) * tau;         // giros acumulados, como en la página
  if (indexAt(rot) !== k) fuera++;
  gana[k]++;
}
let chi = 0;
current.forEach((p, i) => { const e = N * p.t / total; chi += (gana[i] - e) ** 2 / e; });
const gl = current.length - 1;
// valor crítico chi-cuadrado al 99,9% (aproximación de Wilson-Hilferty)
const z = 3.0902, crit = gl * Math.pow(1 - 2 / (9 * gl) + z * Math.sqrt(2 / (9 * gl)), 3);
console.log(`Lotería: ${LOT.nombre}. Personas en la ruleta: ${current.length} (sin ${[...EXCLUIDAS].join(", ")}; ${MINIMO > 1 ? `desde ${MINIMO} ${LOT.unidad || "tickets"}` : "sin 0 tickets"})`);
console.log(`Sorteos simulados: ${N.toLocaleString("es-CO")}`);
console.log(`Flecha fuera de la casilla del sorteado: ${fuera}`);
console.log(`Chi-cuadrado: ${chi.toFixed(1)} con ${gl} grados de libertad (límite al 99,9%: ${crit.toFixed(1)}) -> ${chi < crit ? "proporcional a los tickets" : "REVISAR"}`);
const orden = current.map((p, i) => ({ p, i })).sort((a, b) => b.p.t - a.p.t);
const fila = ({ p, i }) => `  ${p.n.padEnd(32)} ${String(p.t).padStart(5)} ${LOT.unidad || "tickets"}  esperado ${(100 * p.t / total).toFixed(3)}%  obtenido ${(100 * gana[i] / N).toFixed(3)}%`;
console.log("Más tickets:"); orden.slice(0, 3).forEach(r => console.log(fila(r)));
console.log("Menos tickets:"); orden.slice(-3).forEach(r => console.log(fila(r)));
process.exit(fuera === 0 && chi < crit ? 0 : 1);
