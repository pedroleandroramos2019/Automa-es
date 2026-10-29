/* Renderiza os posts únicos de uma data em PNG 1080×1350.
   Uso: node posts/gerar.mjs 2026-10-29
        → posts/2026-10-29/src/NN-autor-tema.html  vira  posts/2026-10-29/NN-autor-tema.png
   Com --miniatura, gera também miniaturas/NN-...-300px.png para o teste de legibilidade. */

import { createRequire } from 'node:module';
import { existsSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const { chromium } = createRequire(import.meta.url)('playwright');

const RAIZ = fileURLToPath(new URL('.', import.meta.url));
const data = process.argv.slice(2).find((a) => !a.startsWith('--'));
const miniatura = process.argv.includes('--miniatura');

if (!data || !existsSync(join(RAIZ, data, 'src'))) {
  console.error('Uso: node posts/gerar.mjs AAAA-MM-DD [--miniatura]');
  process.exit(1);
}

const pasta = join(RAIZ, data);
const arquivos = readdirSync(join(pasta, 'src')).filter((f) => f.endsWith('.html')).sort();

const executablePath = ['/opt/pw-browsers/chromium', process.env.PLAYWRIGHT_CHROMIUM_PATH].find((c) => c && existsSync(c));
const navegador = await chromium.launch(executablePath ? { executablePath } : {});
const pagina = await navegador.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });

for (const arquivo of arquivos) {
  await pagina.goto(pathToFileURL(join(pasta, 'src', arquivo)).href, { waitUntil: 'load' });
  await pagina.evaluate(() => document.fonts.ready);
  const semRetrato = await pagina.evaluate(() => document.querySelector('.post').classList.contains('sem-retrato'));
  const nome = arquivo.replace(/\.html$/, '');
  const saida = join(pasta, `${nome}.png`);
  await pagina.locator('.post').screenshot({ path: saida });
  console.log(`${nome}.png${semRetrato ? '  (sem retrato: versão tipográfica)' : ''}`);

  if (miniatura) {
    mkdirSync(join(pasta, 'miniaturas'), { recursive: true });
    const mini = await navegador.newPage({ viewport: { width: 300, height: 375 } });
    await mini.setContent(`<body style="margin:0"><img src="data:image/png;base64,${readFileSync(saida).toString('base64')}" width="300"></body>`);
    await mini.screenshot({ path: join(pasta, 'miniaturas', `${nome}-300px.png`) });
    await mini.close();
  }
}

await navegador.close();
