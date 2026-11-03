"""Confere assets publicados dos Releases das coleções oficiais IGETech.

Consulta somente a API de leitura do GitHub, nunca baixa nem executa livros.
Confere existência, tamanho e digest sha256 quando a API o disponibiliza.
O cliente VenusBiblio verifica SHA-256 do próprio arquivo no download.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

REPO = "IGETech01/VenusBiblio-Colecoes"
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "workshop" / "colecoes.json"
TAG = re.compile(r"colecao-[a-z0-9][a-z0-9-]{0,62}-v[1-9][0-9]{0,5}\Z")
MAX_BOOK = 250 * 1024 * 1024
MAX_RESPONSE = 4 * 1024 * 1024


def api(path: str) -> object:
    """URL fixa, sem caminhos fornecidos diretamente pelo catálogo."""
    url = f"https://api.github.com/repos/{REPO}/{path}"
    token = os.environ.get("GH_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "VenusBiblio-Collections-CI",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("Resposta inesperada da API do GitHub")
            data = response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE:
                raise ValueError("Resposta da API maior que 4 MiB")
            return json.loads(data)
    except urllib.error.HTTPError as exc:
        raise ValueError(f"Falha consultando Release na API GitHub (HTTP {exc.code})") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ValueError("Falha de conexão consultando GitHub Releases") from exc


def published_assets(tag: str) -> dict[str, dict]:
    if not isinstance(tag, str) or not TAG.fullmatch(tag):
        raise ValueError("Tag de coleção inválida")
    release = api(f"releases/tags/{quote(tag, safe='')}")
    if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
        raise ValueError(f"Release da coleção não está publicado: {tag}")
    ident = release.get("id")
    if type(ident) is not int or ident <= 0 or release.get("tag_name") != tag:
        raise ValueError(f"Metadados inválidos do Release: {tag}")

    assets = {}
    for page in range(1, 12):
        items = api(f"releases/{ident}/assets?per_page=100&page={page}")
        if not isinstance(items, list):
            raise ValueError(f"Lista de arquivos inválida: {tag}")
        for entry in items:
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
                raise ValueError(f"Asset inválido no Release: {tag}")
            name = entry["name"]
            if name.casefold() in assets:
                raise ValueError(f"Asset duplicado no Release: {tag}")
            assets[name.casefold()] = entry
        if len(items) < 100:
            return assets
    raise ValueError(f"Release com arquivos demais: {tag}")


def verify_asset(tag: str, asset: dict, book: dict) -> bool:
    path = book["arquivo"]
    if not isinstance(path, str) or not path.startswith("livros/"):
        raise ValueError("Caminho de livro inválido")
    name = path[7:]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}\.(?:pdf|epub|cbz)", name, re.I):
        raise ValueError("Nome de livro inválido")
    if asset.get("name") != name or asset.get("state") != "uploaded":
        raise ValueError(f"Asset ausente ou incompleto no Release {tag}: {name}")
    size = book.get("tamanho")
    if type(size) is not int or not (0 < size <= MAX_BOOK) or asset.get("size") != size:
        raise ValueError(f"Tamanho diferente do catálogo: {name}")
    digest = book.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch("[a-fA-F0-9]{64}", digest):
        raise ValueError(f"SHA-256 inválido no catálogo: {name}")
    github_digest = asset.get("digest")
    if github_digest is not None:
        if not isinstance(github_digest, str) or github_digest.lower() != "sha256:" + digest.lower():
            raise ValueError(f"SHA-256 declarado pelo GitHub diverge: {name}")
        return True
    return False


def validate() -> int:
    idx = json.loads(INDEX.read_text(encoding="utf-8-sig"))
    if not isinstance(idx, dict) or idx.get("formato") != "igetech-workshop-colecoes-v1":
        raise ValueError("Índice de coleções inválido")
    entries = idx.get("colecoes")
    if not isinstance(entries, list) or len(entries) > 50:
        raise ValueError("Número de coleções inválido")
    if not entries:
        print("OK: sem coleções publicadas; verificação remota desnecessária.")
        return 0

    by_tag: dict[str, list[dict]] = {}
    for item in entries:
        if not isinstance(item, dict) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", str(item.get("id", ""))):
            raise ValueError("ID de coleção inválido")
        slug = item["id"]
        doc = json.loads((ROOT / "workshop" / "colecoes" / slug / "catalogo.json").read_text(encoding="utf-8-sig"))
        distrib = doc.get("distribuicao", {})
        if (not isinstance(distrib, dict) or distrib.get("tipo") != "github_release"
                or distrib.get("repositorio") != REPO):
            raise ValueError(f"Distribuição externa não autorizada: {slug}")
        tag = distrib.get("tag")
        if not isinstance(tag, str) or tag != "colecao-" + slug + "-v" + tag.rsplit("-v", 1)[-1] or not TAG.fullmatch(tag):
            raise ValueError(f"Tag inválida para {slug}")
        livros = doc.get("livros")
        if not isinstance(livros, list) or not livros:
            raise ValueError(f"Catálogo sem livros: {slug}")
        by_tag.setdefault(tag, []).extend(livros)

    total = 0
    complete = 0
    for tag, books in by_tag.items():
        remote = published_assets(tag)
        expected = set()
        for book in books:
            if not isinstance(book, dict) or not isinstance(book.get("arquivo"), str):
                raise ValueError(f"Livro inválido no catálogo: {tag}")
            filename = book["arquivo"].removeprefix("livros/")
            key = filename.casefold()
            if key in expected:
                raise ValueError(f"Asset duplicado no catálogo: {filename}")
            expected.add(key)
            asset = remote.get(key)
            if asset is None:
                raise ValueError(f"Asset anunciado não foi publicado: {filename}")
            complete += bool(verify_asset(tag, asset, book))
            total += 1
        if set(remote) != expected:
            raise ValueError(f"Release contém arquivos não declarados no catálogo: {tag}")

    print(f"OK: {len(by_tag)} Releases de coleções, {total} assets conferidos; "
          f"{complete} com digest SHA-256 fornecido pelo GitHub.")
    if complete < total:
        print("Aviso: digests ausentes na API serão verificados pelo cliente ao baixar o livro.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(validate())
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError, KeyError) as err:
        print("RELEASE REPROVADO:", err, file=sys.stderr)
        raise SystemExit(1)
