/* Preenche os slots de imagem e o selo do perfil a partir de /config.json.
   Enquanto um arquivo de imagem não existir em /imagens, o slot mostra um
   marcador de trabalho dizendo exatamente qual arquivo falta. */

const SELO_PADRAO = `
<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.1"
     stroke-linecap="round" stroke-linejoin="round" aria-label="Café no Copo Americano">
  <path d="M19.6 13.4c0-2.6 2.2-3.1 2.2-5.5 0-1.4-.8-2.3-1.5-2.8"/>
  <path d="M26.6 13.4c0-2.6 2.2-3.1 2.2-5.5 0-1.4-.8-2.3-1.5-2.8"/>
  <path d="M12.4 18.2h20.2l-2.2 12.5a4.1 4.1 0 0 1-4 3.4h-7.8a4.1 4.1 0 0 1-4-3.4z"/>
  <path d="M32.6 21.4c3.6 0 5.7 1.9 5.7 4.5s-2.1 4.4-5.3 4.4"/>
  <path d="M10 38.4c2.9 1.9 8.1 2.9 14 2.9s11.1-1 14-2.9"/>
</svg>`;

const carrega = (src) => new Promise((ok) => {
  const img = new Image();
  img.onload = () => ok(img);
  img.onerror = () => ok(null);
  img.src = src;
});

window.__pronto = (async () => {
  const config = await fetch('../config.json').then((r) => r.json());

  for (const selo of document.querySelectorAll('[data-selo]')) {
    selo.innerHTML = config.selo
      ? `<img src="../imagens/${config.selo}" alt="">`
      : SELO_PADRAO;
  }

  await Promise.all([...document.querySelectorAll('[data-imagem]')].map(async (slot) => {
    const n = slot.dataset.imagem;
    const ficha = config.cards[n] || {};
    const arquivo = ficha.arquivo || (config.cards[ficha.usa] || {}).arquivo;

    slot.style.setProperty('--enquadramento', ficha.enquadramento || '50% 50%');
    slot.style.setProperty('--zoom', ficha.zoom || 1);

    const img = arquivo ? await carrega(`../imagens/${arquivo}`) : null;
    if (img) {
      img.className = 'imagem__foto';
      img.alt = ficha.descricao || '';
      slot.prepend(img);
      return;
    }

    const vazio = document.createElement('div');
    vazio.className = 'imagem__vazio';
    vazio.innerHTML = `<b>imagem pendente</b>
      <code>imagens/${arquivo || '—'}</code>
      <small>${ficha.descricao || ''}</small>`;
    slot.prepend(vazio);
  }));

  await document.fonts.ready;
  document.documentElement.dataset.pronto = '1';
})();
