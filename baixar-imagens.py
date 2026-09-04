#!/usr/bin/env python3
"""Baixa do Wikimedia Commons as obras de domínio público do carrossel.

    python3 baixar-imagens.py            # baixa tudo
    python3 baixar-imagens.py --listar   # mostra os candidatos sem baixar

Roda na sua máquina — o ambiente onde o projeto foi montado tem a saída de
rede bloqueada para o Wikimedia. Para cada card o script tenta os arquivos
conhecidos em ordem e, se nenhum servir, busca no Commons; descarta o que
estiver abaixo de 1080 px de largura e fica com a maior resolução. Salva em
imagens/ com os nomes que o config.json espera e imprime autor, data e
licença de cada imagem, para conferir contra as legendas dos cards.
"""

import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request

API = 'https://commons.wikimedia.org/w/api.php'
UA = 'CarrosselCafeNoCopoAmericano/1.0 (script de uso proprio; contato via GitHub)'
RAIZ = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(RAIZ, 'imagens')
LARGURA_MIN = 1080   # o card exibe em 1080; abaixo disso a imagem sobe borrada
LARGURA_ALVO = 2000  # folga para reenquadrar sem baixar arquivos enormes

ALVOS = [
    {
        'destino': 'card-1-tolstoi-repin-1887.jpg',
        'obra': 'Retrato de Liev Tolstói — Iliá Répin, 1887',
        'candidatos': [
            'File:Ilya Efimovich Repin (1844-1930) - Portrait of Leo Tolstoy (1887).jpg',
        ],
        'busca': 'Repin portrait Leo Tolstoy 1887',
    },
    {
        'destino': 'card-2-familia-iasnaia-poliana.jpg',
        'obra': 'Tolstói com a família em Iásnaia Poliana',
        'candidatos': [
            'File:Tolstoy family circle at Yasnaya Polyana.jpg',
            'File:Leo Tolstoy with family in Yasnaya Polyana.jpg',
        ],
        'busca': 'Tolstoy family Yasnaya Polyana photograph',
        'atencao': 'A legenda do card diz "fotografia, c. 1887". Confira a data '
                   'impressa acima: se não bater, escolha outra imagem com '
                   '--arquivo ou ajuste a legenda em src/carrossel.html. '
                   'O prompt original previa como alternativa uma fotografia '
                   'da propriedade (exterior da casa).',
    },
    {
        'destino': 'card-3-ge-o-que-e-a-verdade-1890.jpg',
        'obra': 'O Que É a Verdade? (Cristo e Pilatos) — Nikolai Gué, 1890',
        'candidatos': ['File:What is truth.jpg'],
        'busca': 'Nikolai Ge What is truth Christ Pilate 1890',
    },
    {
        'destino': 'card-4-miassoiedov-ceifeiros-1887.jpg',
        'obra': 'Tempo de Colheita (Os Ceifeiros) — Grigóri Miassoiédov, 1887',
        'candidatos': [
            # reprodução chapada da tela, sem moldura nem parede de museu
            'File:Grigorij Grigorjewitsch Mjassojedow 003.jpg',
            'File:Harvest time (Croppers) by Grigory Myasoedov in the State Russian Museum IMG 4818.jpg',
        ],
        'busca': 'Myasoyedov harvest time croppers 1887',
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


def limpar(html):
    return re.sub(r'<[^>]+>', '', html or '').strip() or '—'


def fichas(titulos):
    """Metadados dos arquivos pedidos, na ordem em que foram passados."""
    if not titulos:
        return []
    dados = api(titles='|'.join(titulos), prop='imageinfo',
                iiprop='url|size|extmetadata', iiurlwidth=LARGURA_ALVO)
    query = dados.get('query', {})
    # a API normaliza títulos; refaz o mapa para não perder correspondência
    paginas = {p.get('title'): p for p in query.get('pages', {}).values()}
    saida = []
    for p in paginas.values():
        if 'missing' in p or not p.get('imageinfo'):
            continue
        info = p['imageinfo'][0]
        meta = info.get('extmetadata', {})
        campo = lambda k: (meta.get(k) or {}).get('value', '')
        saida.append({
            'titulo': p['title'],
            'url': info.get('thumburl') or info['url'],
            'largura': info.get('thumbwidth') or info['width'],
            'altura': info.get('thumbheight') or info['height'],
            'original': (info['width'], info['height']),
            'autor': limpar(campo('Artist')),
            'data': limpar(campo('DateTimeOriginal')),
            'licenca': limpar(campo('LicenseShortName')),
            'pagina': info['descriptionurl'],
        })
    return saida


def buscar(termo, limite=12):
    dados = api(list='search', srsearch=termo, srnamespace=6, srlimit=limite)
    return [m['title'] for m in dados.get('query', {}).get('search', [])]


def candidatos(alvo):
    """Fichas utilizáveis, das de maior para as de menor resolução original."""
    achados = fichas(alvo['candidatos'])
    if not any(f['original'][0] >= LARGURA_MIN for f in achados) and alvo.get('busca'):
        extras = [t for t in buscar(alvo['busca']) if t not in alvo['candidatos']]
        achados += fichas(extras[:10])
    return sorted(achados, key=lambda f: f['original'][0], reverse=True)


def baixar(url, caminho):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=300) as r, open(caminho, 'wb') as f:
        f.write(r.read())
    return os.path.getsize(caminho)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--listar', action='store_true',
                   help='mostra os candidatos de cada card, com resolução e data')
    p.add_argument('--card', type=int, choices=[1, 2, 3, 4], help='age só sobre um card')
    p.add_argument('--arquivo', help='usa este arquivo do Commons (requer --card)')
    args = p.parse_args()

    if args.arquivo and not args.card:
        p.error('--arquivo precisa vir junto de --card')

    os.makedirs(DESTINO, exist_ok=True)
    pendentes = []

    for i, alvo in enumerate(ALVOS, 1):
        if args.card and i != args.card:
            continue
        print(f'\n── Card {i} · {alvo["obra"]}')

        try:
            if args.arquivo:
                titulo = args.arquivo if args.arquivo.startswith('File:') else f'File:{args.arquivo}'
                achados = fichas([titulo])
            else:
                achados = candidatos(alvo)
        except (urllib.error.URLError, OSError) as e:
            print(f'   ⚠ não deu para falar com o Commons: {rede(e)}')
            pendentes.append(i)
            continue

        servem = [f for f in achados if f['original'][0] >= LARGURA_MIN]

        if args.listar:
            if not achados:
                print('   nenhum candidato encontrado')
            for f in achados:
                marca = '  ' if f in servem else '✗ '
                print(f'   {marca}{f["titulo"]}')
                print(f'       {f["original"][0]}×{f["original"][1]}   {f["data"]}')
            if achados and not servem:
                print(f'   ⚠ nenhum chega aos {LARGURA_MIN} px de largura mínimos')
            continue

        if not servem:
            menor = achados[0]['original'][0] if achados else 0
            print(f'   ⚠ nada com pelo menos {LARGURA_MIN} px de largura'
                  + (f' (maior encontrado: {menor} px)' if menor else ''))
            print('     Rode com --listar para ver as opções.')
            pendentes.append(i)
            continue

        f = servem[0]
        caminho = os.path.join(DESTINO, alvo['destino'])
        try:
            tam = baixar(f['url'], caminho)
        except (urllib.error.URLError, OSError) as e:
            print(f'   ⚠ falhou o download: {rede(e)}')
            pendentes.append(i)
            continue

        print(f'   ✓ imagens/{alvo["destino"]}  {f["largura"]}×{f["altura"]}  {tam/1024:.0f} KB')
        print(f'     arquivo: {f["titulo"]}')
        print(f'     autor:   {f["autor"]}')
        print(f'     data:    {f["data"]}')
        print(f'     licença: {f["licenca"]}')
        print(f'     origem:  {f["pagina"]}')
        if alvo.get('atencao'):
            print(f'     ⚠ {alvo["atencao"]}')

    if args.listar:
        return 0

    if pendentes:
        print(f'\nFaltam os cards {", ".join(map(str, pendentes))}. '
              'Rode `python3 baixar-imagens.py --listar` para ver as opções.')
        return 1

    print('\nTudo baixado. Agora rode `npm run build` para gerar os PNGs.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
