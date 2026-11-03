"""Verifica apenas metadados públicos do Workshop VenusBiblio (sem credenciais)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSHOP = ROOT / 'workshop'
FORMATO_INDICE = 'igetech-workshop-colecoes-v1'
FORMATO_CATALOGO = 'biblioteca-offline-workshop-v1'
REPO = 'IGETech01/VenusBiblio-Colecoes'
MAX_JSON = 2 * 1024 * 1024
MAX_BOOK = 250 * 1024 * 1024
MAX_COVER = 2 * 1024 * 1024
SLUG = re.compile(r'[a-z0-9][a-z0-9-]{0,62}\Z')
BOOK = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,159}\.(?:pdf|epub|cbz)\Z', re.I)
COVER = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,159}\.(?:jpg|jpeg|png|webp)\Z', re.I)
SHA256 = re.compile(r'[a-fA-F0-9]{64}\Z')
BOOK_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z')


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def text_ok(value: object, limit: int, required: bool = True) -> bool:
    return isinstance(value, str) and (bool(value.strip()) or not required) and len(value) <= limit and not any(c in value for c in '\x00\r')


def strict_object(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('Chave JSON duplicada: ' + k)
        d[k] = v
    return d


def load_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f'JSON ausente/inseguro: {path}')
    require(path.stat().st_size <= MAX_JSON, f'JSON maior que 2 MiB: {path}')
    data = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=strict_object)
    require(isinstance(data, dict), f'Objeto JSON esperado: {path}')
    return data


def cover_exists(folder: Path, name: object) -> bool:
    if not name:
        return True
    if not isinstance(name, str) or not name.startswith('capas/'):
        return False
    parts = name.split('/')
    if len(parts) != 2 or not COVER.fullmatch(parts[1]):
        return False
    obj = folder / 'capas' / parts[1]
    return obj.is_file() and not obj.is_symlink() and obj.stat().st_size <= MAX_COVER


def validate_collection(slug: str, metadata: dict) -> int:
    folder = WORKSHOP / 'colecoes' / slug
    require(folder.is_dir() and not folder.is_symlink(), f'Pasta inexistente: {slug}')
    doc = load_json(folder / 'catalogo.json')
    require(doc.get('formato') == FORMATO_CATALOGO, f'Formato do catálogo incorreto: {slug}')
    require(set(doc) <= {'formato', 'nome', 'descricao', 'livros', 'distribuicao'}, f'Campos extras no catálogo público: {slug}')
    require(text_ok(doc.get('nome'), 100), f'Nome do catálogo inválido: {slug}')
    require(text_ok(doc.get('descricao', ''), 600, False), f'Descrição inválida: {slug}')
    require(metadata['nome'].strip() == doc['nome'].strip(), f'Nome do índice não corresponde: {slug}')
    require(metadata['descricao'].strip() == doc.get('descricao', '').strip(), f'Descrição do índice não corresponde: {slug}')

    distrib = doc.get('distribuicao')
    require(isinstance(distrib, dict) and set(distrib) == {'tipo', 'repositorio', 'tag'}, f'Distribuição incorreta: {slug}')
    require(distrib['tipo'] == 'github_release' and distrib['repositorio'] == REPO, f'Repositório inválido: {slug}')
    require(bool(re.fullmatch(r'colecao-' + re.escape(slug) + r'-v[1-9][0-9]{0,5}', str(distrib['tag']))), f'Tag inválida: {slug}')

    books = doc.get('livros')
    require(isinstance(books, list) and 0 < len(books) <= 1000, f'Lista de livros inválida/vazia: {slug}')
    require(len(books) == metadata['quantidade'], f'Quantidade divergente: {slug}')
    ids, names = set(), set()
    for item in books:
        require(isinstance(item, dict), f'Livro inválido: {slug}')
        require(set(item) <= {'id','titulo','autor','genero','ano','licenca','arquivo','sha256','tamanho','descricao','tipo_conteudo','capa'}, f'Campos extras no livro da coleção: {slug}')
        id_ = item.get('id')
        require(isinstance(id_, str) and bool(BOOK_ID.fullmatch(id_)) and id_ not in ids, f'ID de livro inválido/duplicado: {slug}')
        ids.add(id_)
        for field, limit in [('titulo', 220), ('autor', 220), ('genero', 80), ('licenca', 150)]:
            require(text_ok(item.get(field), limit), f'Campo {field} inválido: {slug}/{id_}')
        require(text_ok(item.get('descricao', ''), 1000, False), f'Descrição de livro inválida: {slug}/{id_}')
        year = item.get('ano')
        require(year is None or (type(year) is int and 0 <= year <= 2200), f'Ano inválido: {slug}/{id_}')
        size = item.get('tamanho')
        require(type(size) is int and 0 < size <= MAX_BOOK, f'Tamanho inválido: {slug}/{id_}')
        require(isinstance(item.get('sha256'), str) and bool(SHA256.fullmatch(item['sha256'])), f'SHA-256 inválido: {slug}/{id_}')
        path = item.get('arquivo')
        require(isinstance(path, str) and path.startswith('livros/') and len(path.split('/')) == 2 and bool(BOOK.fullmatch(path[7:])), f'Asset inválido: {slug}/{id_}')
        require(path[7:].casefold() not in names, f'Asset duplicado: {slug}/{id_}')
        names.add(path[7:].casefold())
        kind = item.get('tipo_conteudo', 'HQ' if path.lower().endswith('.cbz') else 'Livro')
        require((path.lower().endswith('.cbz') and kind in ('Mangá', 'HQ')) or
                (not path.lower().endswith('.cbz') and kind == 'Livro'), f'Tipo de conteúdo inválido: {slug}/{id_}')
        require(cover_exists(folder, item.get('capa', '')), f'Capa ausente/insegura: {slug}/{id_}')
    return len(books)


def validate() -> int:
    idx = load_json(WORKSHOP / 'colecoes.json')
    require(idx.get('formato') == FORMATO_INDICE, 'Formato do índice não corresponde ao VenusBiblio')
    require(set(idx) == {'formato', 'colecoes'}, 'Campos extras no índice público')
    items = idx.get('colecoes')
    require(isinstance(items, list) and len(items) <= 50, 'Índice com mais de 50 coleções')
    seen = set()
    count = 0
    for meta in items:
        require(isinstance(meta, dict), 'Entrada do índice inválida')
        require(set(meta) == {'id','nome','descricao','quantidade'}, 'Campos extras na entrada do índice')
        slug = meta.get('id')
        require(isinstance(slug, str) and bool(SLUG.fullmatch(slug)) and slug.lower() not in seen, 'ID de coleção inválido/duplicado')
        seen.add(slug.lower())
        require(text_ok(meta.get('nome'), 100), f'Nome inválido: {slug}')
        require(text_ok(meta.get('descricao', ''), 600, False), f'Descrição inválida: {slug}')
        n = meta.get('quantidade')
        require(type(n) is int and 0 < n <= 1000, f'Quantidade inválida: {slug}')
        count += validate_collection(slug, meta)
    folder = WORKSHOP / 'colecoes'
    if folder.exists():
        for item in folder.iterdir():
            require(item.is_dir() and not item.is_symlink() and item.name in seen, f'Coleção não indexada ou arquivo inesperado: {item.name}')
            for entry in item.rglob('*'):
                require(not entry.is_symlink(), f'Link simbólico não permitido: {entry}')
                if entry.is_file():
                    relative = entry.relative_to(item).as_posix()
                    if relative != 'catalogo.json' and not (relative.startswith('capas/') and len(relative.split('/')) == 2 and COVER.fullmatch(relative.split('/')[1])):
                        raise ValueError(f'Arquivo inesperado no Workshop: {relative}')
    for entry in ROOT.rglob('*'):
        if any(part in ('.git', '__pycache__', '.venv') for part in entry.relative_to(ROOT).parts) or not entry.is_file():
            continue
        require(entry.suffix.lower() not in ('.pdf', '.epub', '.cbz', '.zip', '.exe', '.pem', '.key', '.db', '.sqlite'), f'Arquivo privado/binário não permitido no Git: {entry.relative_to(ROOT)}')
    print(f'OK: {len(items)} coleções públicas, {count} obras catalogadas. Nenhum livro armazenado nos commits.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(validate())
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print('CATÁLOGO REPROVADO:', exc, file=sys.stderr)
        sys.exit(1)
