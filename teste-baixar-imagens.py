"""Testa a logica de selecao do baixar-imagens.py com respostas simuladas.

    python3 teste-baixar-imagens.py

Nao toca na rede: troca a funcao api() por respostas de mentira e confere
que a escolha de arquivo se comporta - prioridade declarada acima da
resolucao, filtro de largura minima, e recurso a busca so quando nenhum
arquivo conhecido serve.
"""
import importlib.util, sys, os
AQUI = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bx', os.path.join(AQUI, 'baixar-imagens.py'))
bx = importlib.util.module_from_spec(spec); spec.loader.exec_module(bx)

def pagina(titulo, w, h, data='1887', autor='Autor X'):
    return {'title': titulo, 'imageinfo': [{
        'url': f'https://upload.wikimedia.org/{titulo}', 'width': w, 'height': h,
        'thumburl': f'https://upload.wikimedia.org/thumb/{titulo}',
        'thumbwidth': min(w, bx.LARGURA_ALVO),
        'thumbheight': int(h * min(w, bx.LARGURA_ALVO) / w),
        'descriptionurl': f'https://commons.wikimedia.org/wiki/{titulo}',
        'extmetadata': {'Artist': {'value': f'<a href="#">{autor}</a>'},
                        'DateTimeOriginal': {'value': data},
                        'LicenseShortName': {'value': 'Public domain'}}}]}

falhas = []
def checar(nome, cond, detalhe=''):
    print(('  ok   ' if cond else '  FALHA ') + nome + ('' if cond else f'  → {detalhe}'))
    if not cond: falhas.append(nome)

# 1. arquivo confirmado e grande o bastante: usa ele, sem busca
buscou = []
bx.api = lambda **p: (buscou.append(p) if 'srsearch' in p else None) or (
    {'query': {'pages': {'1': pagina('File:Bom.jpg', 2400, 1600)}}} if 'titles' in p
    else {'query': {'search': []}})
c = bx.candidatos({'candidatos': ['File:Bom.jpg'], 'busca': 'x'})
checar('usa o arquivo confirmado', len(c) == 1 and c[0]['largura'] == 2000, c)
checar('nao busca quando o confirmado serve', not buscou, buscou)
checar('limpa HTML do autor', c[0]['autor'] == 'Autor X', c[0]['autor'])

# 2. confirmado pequeno demais: cai na busca e escolhe a maior
def api2(**p):
    if 'srsearch' in p:
        return {'query': {'search': [{'title': 'File:Grande.jpg'}, {'title': 'File:Media.jpg'}]}}
    titulos = p['titles'].split('|')
    tam = {'File:Pequeno.jpg': (568, 397), 'File:Grande.jpg': (3000, 2000),
           'File:Media.jpg': (1200, 900)}
    return {'query': {'pages': {str(i): pagina(t, *tam[t]) for i, t in enumerate(titulos)}}}
bx.api = api2
c = bx.candidatos({'candidatos': ['File:Pequeno.jpg'], 'busca': 'x'})
checar('busca quando o confirmado e pequeno', len(c) == 3, len(c))
checar('conhecido primeiro, busca ordenada por resolucao',
       [f['titulo'] for f in c] == ['File:Pequeno.jpg', 'File:Grande.jpg', 'File:Media.jpg'],
       [f['titulo'] for f in c])
servem = [f for f in c if f['original'][0] >= bx.LARGURA_MIN]
checar('filtra abaixo de 1080px', len(servem) == 2 and servem[0]['titulo'] == 'File:Grande.jpg', servem)

# NOVO: entre conhecidos que servem, vale a ordem declarada, nao a resolucao.
# E o caso do card 4: a foto da tela no museu tem mais pixels e e pior.
def api3(**p):
    if 'srsearch' in p: raise AssertionError('nao devia buscar: os conhecidos servem')
    tam = {'File:Reproducao.jpg': (2156, 1250), 'File:FotoNoMuseu.jpg': (4032, 3024)}
    titulos = p['titles'].split('|')
    return {'query': {'pages': {str(i): pagina(t, *tam[t]) for i, t in enumerate(titulos)}}}
bx.api = api3
c = bx.candidatos({'candidatos': ['File:Reproducao.jpg', 'File:FotoNoMuseu.jpg'], 'busca': 'x'})
checar('respeita a ordem declarada acima da resolucao',
       c[0]['titulo'] == 'File:Reproducao.jpg', [f['titulo'] for f in c])

# titulo normalizado pela API (underscore -> espaco) nao perde a prioridade
def api4(**p):
    tam = {'File:A B.jpg': (2000, 1500), 'File:Z.jpg': (3000, 2000)}
    titulos = [t.replace('_', ' ') for t in p['titles'].split('|')]
    return {'query': {'pages': {str(i): pagina(t, *tam[t]) for i, t in enumerate(titulos)}}}
bx.api = api4
c = bx.candidatos({'candidatos': ['File:A_B.jpg', 'File:Z.jpg'], 'busca': 'x'})
checar('normaliza underscore ao ordenar', c[0]['titulo'] == 'File:A B.jpg',
       [f['titulo'] for f in c])

# 3. thumb limitado a LARGURA_ALVO, sem ampliar o que e menor
bx.api = lambda **p: {'query': {'pages': {'1': pagina('File:P.jpg', 1400, 1000)}}}
f = bx.fichas(['File:P.jpg'])[0]
checar('nao amplia acima do original', f['largura'] == 1400, f['largura'])

# 4. arquivo inexistente nao quebra
bx.api = lambda **p: {'query': {'pages': {'-1': {'title': 'File:X.jpg', 'missing': ''}}}}
checar('ignora arquivo ausente', bx.fichas(['File:X.jpg']) == [])

# 5. erro de rede vira mensagem legivel
import urllib.error
msg = bx.rede(urllib.error.URLError('Tunnel connection failed: 403 Forbidden'))
checar('traduz bloqueio de rede', 'proxy ou firewall' in msg, msg)

print(f"\n{'todos os testes passaram' if not falhas else str(len(falhas)) + ' falha(s)'}")
sys.exit(1 if falhas else 0)

