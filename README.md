# Carrossel — "A Confissão", de Liev Tolstói

Cinco cards de 1080 × 1350 px para Instagram, montados sobre a **Identidade
Visual v2** do *Café no Copo Americano*. O layout é HTML/CSS e a exportação em
PNG é feita por um Chromium headless, então o resultado é idêntico a cada
rodada e o texto continua editável (nada é achatado em imagem antes da hora).

```bash
npm install
npm run build      # gera out/card-1.png … out/card-5.png
npm run preview    # abre o carrossel no navegador para conferir antes de exportar
```

---

## ⚠️ Faltam as 4 imagens

**Os cards já estão prontos, mas saem com um marcador escuro no lugar das
fotos.** O ambiente onde este projeto foi montado tem a saída de rede
restrita a uma lista curta de domínios — Wikimedia Commons, Wikipédia e os
sites de museu estão bloqueados —, então não foi possível baixar as obras de
domínio público. Todo o resto está feito: basta colocar os arquivos em
`imagens/` com os nomes abaixo e rodar `npm run build` de novo.

| Arquivo esperado em `imagens/` | Obra | Busca |
|---|---|---|
| `card-1-tolstoi-repin-1887.jpg` | *Retrato de Liev Tolstói* — Iliá Répin, 1887 (Galeria Tretiakov) | `Ilya Repin Tolstoy portrait 1887 Wikimedia` |
| `card-2-familia-iasnaia-poliana.jpg` | Tolstói com a família em Iásnaia Poliana — fotografia, c. 1887 | `Tolstoy family Yasnaya Polyana photograph Wikimedia` |
| `card-3-ge-o-que-e-a-verdade-1890.jpg` | *O Que É a Verdade? (Cristo e Pilatos)* — Nikolai Gué, 1890 | `Nikolai Ge What is Truth painting Wikimedia` |
| `card-4-miassoiedov-ceifeiros-1887.jpg` | *Tempo de Colheita (Os Ceifeiros)* — Grigóri Miassoiédov, 1887 | `Myasoyedov Mowers 1887 painting Wikimedia` |

O card 5 reaproveita a imagem do card 1 na miniatura circular — não precisa de
arquivo próprio.

**Resolução mínima:** 1080 px de largura para os cards 2–4; para o card 1, que
é full bleed em retrato, o ideal é pelo menos 1080 × 1350. As legendas de
crédito já estão escritas nos cards, então as imagens precisam ser exatamente
as obras da tabela.

### Ajustar o enquadramento

`config.json` controla qual parte de cada imagem aparece no corte. O valor de
`enquadramento` é um `object-position` do CSS: o primeiro número é horizontal,
o segundo vertical, ambos de `0%` (topo/esquerda) a `100%` (base/direita).

```json
"1": {
  "arquivo": "card-1-tolstoi-repin-1887.jpg",
  "enquadramento": "50% 30%"
}
```

`50% 30%` centraliza na horizontal e puxa o corte para o alto — bom para
retratos, porque mantém o rosto acima do gradiente. Depois de colocar as
imagens reais, vale rodar `npm run preview` e acertar esses números.

---

## Selo do perfil

Os cards usam um ícone de xícara desenhado em SVG (`src/montar.js`) como
provisório. Para usar o selo real da marca, coloque o arquivo em `imagens/` e
aponte no `config.json`:

```json
"selo": "selo-cafe-no-copo-americano.png"
```

PNG com fundo transparente ou SVG. Ele é renderizado em 58 × 58 px, em bege
sobre a capa e em vinho sobre os cards de fundo claro.

---

## Acentos: uma ressalva sobre a Cormorant Garamond

A identidade pede Cormorant Garamond Italic para o subtítulo da capa, a
citação e o texto de fechamento — e é ela que está em uso. Vale registrar um
detalhe que aparece em português: **a Cormorant desenha os acentos das
minúsculas quase na altura dos acentos das maiúsculas**, o que deixa uma folga
grande entre a letra e o acento. Medindo o arquivo da fonte (em unidades de
em, com 1000 por em):

| | topo do `e` | topo do `ê` | topo do `Ê` | folga sobre o `e` |
|---|---|---|---|---|
| Cormorant Garamond | 399 | 732 | 764 | **333** |
| EB Garamond | 414 | 641 | 822 | 227 |

Na Cormorant o acento minúsculo (732) fica a apenas 32 unidades do maiúsculo
(764); na EB Garamond a diferença é de 181. Na prática isso aparece em
"vo**cê**" no subtítulo da capa e, em menor grau, nos acentos agudos de
"terr**í**vel", "destru**í**do" e "Tolst**ó**i".

Não é um defeito de renderização nem de codificação do texto (que está em NFC)
— é como a fonte foi desenhada. Como é uma decisão de marca, **mantive a
Cormorant como padrão**. Se preferir acentos mais baixos, a EB Garamond já
está embarcada e a troca é uma linha em `src/identidade.css`:

```css
--serifa-display: 'EB Garamond', serif;   /* no lugar de 'Cormorant Garamond' */
```

Vale comparar as duas em `npm run preview` antes de decidir.

---

## O sistema visual

**Paleta** — bege `#F5F0E8`, tinta `#1A1A1A`, vinho `#5C2028`, sépia `#8C7560`.

**Tipografia** — Poppins ExtraBold nos títulos (caixa-alta), DM Sans no corpo e
nas legendas, Cormorant Garamond Italic no subtítulo, na citação e no
fechamento. As três estão em `fonts/` sob a SIL Open Font License, para que a
renderização não dependa de rede.

**O acento vinho aparece em três lugares, e só neles:** o numeral no círculo,
as legendas de crédito e no máximo uma palavra de destaque por card
(`esconder` no card 2, `fé` no card 4; os cards 1, 3 e 5 não têm nenhuma).

**Sem molduras** — nem cantos em L, nem retângulo interno. **Imagens em full
bleed, opacidade total**, nunca em fade. **O gradiente escuro é localizado**:
existe só onde há texto sobre a imagem (o rodapé da capa e a faixa de 190 px
atrás das legendas de crédito), nunca sobre rostos. **Selo do perfil** no canto
superior direito de todos os cards; **seta de swipe** apenas na capa.

**Divisão texto/imagem** nos cards 2–4, dentro da faixa de 50–55% prevista no
guia, com o mesmo respiro (~67 px) entre o fim do texto e o início da imagem:

| Card | Texto | Imagem | % de texto |
|---|---|---|---|
| 2 — O diagnóstico | 680 px | 670 px | 50,4% |
| 3 — A pergunta | 743 px | 607 px | 55,0% |
| 4 — Os camponeses | 708 px | 642 px | 52,4% |

Os cards 3 e 4 têm mais texto e usam o corpo no piso da faixa do guia (34 px,
contra 36 px do card 2) — é o que mantém os três dentro dos 55%.

---

## Estrutura

```
src/carrossel.html    os 5 cards, com o texto de cada um
src/identidade.css    paleta, tipografia e regras do sistema visual
src/montar.js         preenche os slots de imagem e o selo a partir do config
config.json           quais imagens usar e como enquadrar cada uma
build.mjs             renderiza tudo em PNG 1080 × 1350
fonts/                Poppins, DM Sans, Cormorant Garamond e EB Garamond (OFL)
imagens/              ← as 4 obras entram aqui
out/                  os PNGs prontos para publicar
```

Para mudar um texto, edite `src/carrossel.html` e rode `npm run build`. O
`build.mjs` confere se cada card saiu exatamente em 1080 × 1350 e falha se
algum layout estourar, então uma edição que quebre a diagramação não passa
despercebida.
