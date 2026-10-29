# Retratos (opcionais)

Os PNGs desta pasta saíram na **versão tipográfica**, sem retrato. O ambiente
onde foram gerados não alcança o Wikimedia Commons, então nenhuma foto foi
baixada nem teve a licença conferida.

Para incluir os retratos:

1. Baixe uma foto de domínio público de cada autor no Wikimedia Commons e
   confira a licença na página do arquivo. Bons pontos de partida:
   - Fernando Pessoa: fotografia de c. 1914.
   - Fiódor Dostoiévski: fotografia de 1879.
   - Friedrich Nietzsche: fotografia de 1882 (Gustav Schultze).
2. Salve as fotos aqui com estes nomes exatos: `pessoa.jpg`,
   `dostoievski.jpg` e `nietzsche.jpg`.
3. Rode `node posts/gerar.mjs 2026-10-29`.

Com o arquivo presente, o post troca sozinho para o layout com foto em P&B
sépia. Se precisar ajustar o enquadramento, mude o `--enquadramento` da tag
`<img>` no HTML de `src/`.
