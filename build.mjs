/* Renderiza os 5 cards do carrossel em PNG 1080×1350.
   Uso: node build.mjs            → gera out/card-1.png … out/card-5.png
        node build.mjs --servir   → só sobe o servidor local para pré-visualizar */

import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync, mkdirSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = fileURLToPath(new URL('.', import.meta.url));
const LARGURA = 1080;
const ALTURA = 1350;
const CARDS = [1, 2, 3, 4, 5];

/* Alguns ambientes já trazem o Chromium instalado fora do cache do Playwright.
   Se houver um binário conhecido, usamos ele em vez de baixar outro. */
function chromiumLocal() {
  const candidatos = [process.env.PLAYWRIGHT_CHROMIUM_PATH, '/opt/pw-browsers/chromium'];
  return candidatos.find((c) => c && existsSync(c));
}

const TIPOS = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.woff2': 'font/woff2',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.png': 'image/png', '.webp': 'image/webp', '.svg': 'image/svg+xml',
};

function servidor() {
  const app = createServer(async (req, res) => {
    const caminho = join(RAIZ, normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, ''));
    try {
      const corpo = await readFile(caminho);
      res.writeHead(200, { 'content-type': TIPOS[extname(caminho)] || 'application/octet-stream' });
      res.end(corpo);
    } catch {
      res.writeHead(404).end('não encontrado');
    }
  });
  return new Promise((ok) => app.listen(0, '127.0.0.1', () => ok(app)));
}

const app = await servidor();
const base = `http://127.0.0.1:${app.address().port}/src/carrossel.html`;

if (process.argv.includes('--servir')) {
  console.log(`Pré-visualização em ${base}`);
} else {
  mkdirSync(join(RAIZ, 'out'), { recursive: true });

  const executablePath = chromiumLocal();
  const navegador = await chromium.launch(executablePath ? { executablePath } : {});
  const pagina = await navegador.newPage({
    viewport: { width: LARGURA, height: ALTURA },
    deviceScaleFactor: 1,
  });

  /* Imagem ausente já é relatada no fim; o 404 correspondente é só ruído. */
  const avisos = [];
  pagina.on('console', (m) => {
    if (m.type() === 'error' && !m.text().includes('404')) avisos.push(m.text());
  });

  await pagina.goto(base, { waitUntil: 'networkidle' });
  await pagina.waitForFunction(() => document.documentElement.dataset.pronto === '1');

  const pendentes = await pagina.$$eval('.imagem__vazio code', (n) => n.map((e) => e.textContent));

  for (const n of CARDS) {
    const card = pagina.locator(`#card-${n}`);
    const caixa = await card.boundingBox();
    if (Math.round(caixa.width) !== LARGURA || Math.round(caixa.height) !== ALTURA) {
      throw new Error(`card ${n} saiu com ${caixa.width}×${caixa.height}, esperado ${LARGURA}×${ALTURA}`);
    }
    await card.screenshot({ path: join(RAIZ, 'out', `card-${n}.png`) });
    console.log(`out/card-${n}.png  ${LARGURA}×${ALTURA}`);
  }

  await navegador.close();

  if (pendentes.length) {
    console.log(`\n${pendentes.length} imagem(ns) ainda pendente(s) — os cards saíram com o marcador de trabalho:`);
    for (const p of new Set(pendentes)) console.log(`  · ${p}`);
    console.log('Coloque os arquivos em imagens/ e rode `npm run build` de novo.');
  }
  for (const a of avisos) console.warn(`aviso do navegador: ${a}`);
}

if (!process.argv.includes('--servir')) app.close();
