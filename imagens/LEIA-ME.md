# Coloque aqui as 4 imagens do carrossel

O jeito mais rápido é rodar, na raiz do projeto:

```bash
python3 baixar-imagens.py
```

Ele baixa as obras do Wikimedia Commons já com os nomes certos e imprime
autor, data e licença de cada uma. Os arquivos que o `config.json` espera:

- `card-1-tolstoi-repin-1887.jpg`        — Retrato de Liev Tolstói, Iliá Répin, 1887
- `card-2-familia-iasnaia-poliana.jpg`   — Tolstói com a família em Iásnaia Poliana
- `card-3-ge-o-que-e-a-verdade-1890.jpg` — O Que É a Verdade?, Nikolai Gué, 1890
- `card-4-miassoiedov-ceifeiros-1887.jpg` — Tempo de Colheita, Grigóri Miassoiédov, 1887

Todas de domínio público, com pelo menos 1080 px de largura — e 1080 × 1350
no caso do card 1, que ocupa o card inteiro.

Depois, rode `npm run build` na raiz. Os links das obras e as duas ressalvas
(a data da foto do card 2 e a escolha do arquivo do card 4) estão no README
principal.
