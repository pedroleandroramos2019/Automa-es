#!/usr/bin/env python3
"""Baixa do Wikimedia Commons as obras de domínio público do carrossel.

    python3 baixar-imagens.py            # baixa o que está confirmado
    python3 baixar-imagens.py --listar   # mostra os candidatos das categorias

Roda na sua máquina — o ambiente onde o projeto foi montado tem a saída de
rede bloqueada para o Wikimedia. Os arquivos são salvos em imagens/ com os
nomes que o config.json espera, e o script imprime autor, data e licença de
cada um para você conferir contra as legendas de crédito dos cards.
"""

import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'CarrosselCafeNoCopoAmericano/1.0 (script de uso próprio; contato via GitHub)'
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imagens')
LARGURA = 2000  # px — folgado para 1080 de exibição, sem baixar arquivos enormes

# Cada alvo: o arquivo que o config.json espera, e onde achá-lo no Commons.
# 'arquivo_commons' = página de arquivo confirmada.
# 'categoria'       = não deu para confirmar o arquivo exato daqui; use --listar.
ALVOS = [
    {
        'destino': 'card-1-tolstoi-repin-1887.jpg',
        'obra': 'Retrato de Liev Tolstói — Iliá Répin, 1887',
        'arquivo_commons': 'File:Ilya Efimovich Repin (1844-1930) - Portrait of Leo Tolstoy (1887).jpg',
    },
    {
        'destino': 'card-2-familia-iasnaia-poliana.jpg',
        'obra': 'Tolstói com a família em Iásnaia Poliana',
        'arquivo_commons': 'File:Tolstoy family circle at Yasnaya Polyana.jpg',
        'atencao': 'Confira a DATA: a legenda do card diz "c. 1887". Se a foto for '
                   'de outro período, troque a imagem ou ajuste a legenda no '
                   'card 2 (src/carrossel.html).',
        'categoria': 'Category:Photographs of Leo Tolstoy',
    },
    {
        'destino': 'card-3-ge-o-que-e-a-verdade-1890.jpg',
        'obra': 'O Que É a Verdade? (Cristo e Pilatos) — Nikolai Gué, 1890',
        'arquivo_commons': 'File:What is truth.jpg',
    },
    {
        'destino': 'card-4-miassoiedov-ceifeiros-1887.jpg',
        'obra': 'Tempo de Colheita (Os Ceifeiros) — Grigóri Miassoiédov, 1887',
        'categoria': 'Category:Harvest time (Croppers) by Grigoriy Myasoyedov',
        'atencao': 'Não foi possível confirmar o nome exato do arquivo daqui. '
                   'Rode com --listar, escolha a versão de maior resolução e '
                   'passe o nome em --arquivo.',
    },
]


def rede(erro):
    """Traduz a falha de rede para uma linha legível."""
    motivo = getattr(erro, 'reason', erro)
    if '403' in str(motivo) or 'Forbidden' in str(motivo):
        return (f'{motivo} — parece proxy ou firewall bloqueando o Wikimedia. '
                'Rode este script numa rede sem esse bloqueio.')
    return str(motivo)


def api(**params):
    params.update(action='query', format='json')
    req = urllib.request.Request(f'{API}?{urllib.parse.urlencode(params)}',
                                 headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def ficha(titulo):
    """Devolve (url, largura, altura, metadados) de um arquivo do Commons."""
    dados = api(titles=titulo, prop='imageinfo',
                iiprop='url|size|extmetadata', iiurlwidth=LARGURA)
    paginas = dados.get('query', {}).get('pages', {})
    pagina = next(iter(paginas.values()), {})
    if 'missing' in pagina or not pagina.get('imageinfo'):
        return None
    info = pagina['imageinfo'][0]
    meta = info.get('extmetadata', {})
    campo = lambda k: (meta.get(k) or {}).get('value', '—')
    # thumburl respeita a largura pedida; se o original for menor, vem o original
    return (info.get('thumburl') or info['url'],
            info.get('thumbwidth') or info['width'],
            info.get('thumbheight') or info['height'],
            {'autor': campo('Artist'), 'data': campo('DateTimeOriginal'),
             'licenca': campo('LicenseShortName'), 'origem': info['descriptionurl']})


def listar(categoria):
    dados = api(list='categorymembers', cmtitle=categoria, cmtype='file', cmlimit=100)
    return [m['title'] for m in dados.get('query', {}).get('categorymembers', [])]


def limpar(html):
    return re.sub(r'<[^>]+>', '', html).strip()


def baixar(url, caminho):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=180) as r, open(caminho, 'wb') as f:
        f.write(r.read())
    return os.path.getsize(caminho)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--listar', action='store_true',
                   help='lista os arquivos das categorias em vez de baixar')
    p.add_argument('--card', type=int, choices=[1, 2, 3, 4],
                   help='age só sobre um card')
    p.add_argument('--arquivo',
                   help='nome do arquivo no Commons a usar (requer --card)')
    args = p.parse_args()

    if args.arquivo and not args.card:
        p.error('--arquivo precisa vir junto de --card')

    os.makedirs(DESTINO, exist_ok=True)
    alvos = [a for i, a in enumerate(ALVOS, 1) if not args.card or i == args.card]
    pendentes = []

    for i, alvo in enumerate(ALVOS, 1):
        if alvo not in alvos:
            continue
        print(f'\n── Card {i} · {alvo["obra"]}')

        if args.listar:
            cat = alvo.get('categoria')
            if not cat:
                print(f'   arquivo confirmado: {alvo["arquivo_commons"]}')
                continue
            print(f'   {cat}')
            try:
                for t in listar(cat):
                    print(f'     · {t}')
            except (urllib.error.URLError, OSError) as e:
                print(f'   ⚠ não deu para falar com o Commons: {rede(e)}')
            continue

        titulo = (f'File:{args.arquivo}' if args.arquivo and not args.arquivo.startswith('File:')
                  else args.arquivo) or alvo.get('arquivo_commons')
        if not titulo:
            print(f'   ⚠ {alvo["atencao"]}')
            pendentes.append(i)
            continue

        try:
            dados = ficha(titulo)
        except (urllib.error.URLError, OSError) as e:
            print(f'   ⚠ não deu para falar com o Commons: {rede(e)}')
            pendentes.append(i)
            continue

        if not dados:
            print(f'   ⚠ arquivo não encontrado no Commons: {titulo}')
            pendentes.append(i)
            continue

        url, larg, alt, meta = dados
        if larg < 1080:
            print(f'   ⚠ só {larg} px de largura — abaixo do mínimo de 1080. Pulando.')
            pendentes.append(i)
            continue

        caminho = os.path.join(DESTINO, alvo['destino'])
        try:
            tam = baixar(url, caminho)
        except (urllib.error.URLError, OSError) as e:
            print(f'   ⚠ falhou o download: {rede(e)}')
            pendentes.append(i)
            continue
        print(f'   ✓ imagens/{alvo["destino"]}  {larg}×{alt}  {tam/1024:.0f} KB')
        print(f'     autor:   {limpar(meta["autor"])}')
        print(f'     data:    {limpar(meta["data"])}')
        print(f'     licença: {limpar(meta["licenca"])}')
        print(f'     origem:  {meta["origem"]}')
        if alvo.get('atencao'):
            print(f'     ⚠ {alvo["atencao"]}')

    if args.listar:
        return

    if pendentes:
        print(f'\nFaltam os cards {", ".join(map(str, pendentes))}. '
              f'Rode `python3 baixar-imagens.py --listar` para ver os candidatos.')
    else:
        print('\nTudo baixado. Agora rode `npm run build` para gerar os PNGs.')


if __name__ == '__main__':
    sys.exit(main())
