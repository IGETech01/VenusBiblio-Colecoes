"""Regressão offline dos metadados de GitHub Releases (sem rede)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import verificar_releases as mod

TAG = "colecao-classicos-v1"
SHA = "a" * 64


def sample_asset(*, size=123, digest="sha256:" + SHA):
    return {"name": "livro.pdf", "state": "uploaded", "size": size, "digest": digest}


def sample_book(*, size=123, sha=SHA):
    return {"arquivo": "livros/livro.pdf", "tamanho": size, "sha256": sha}


class ReleaseSecurityTest(unittest.TestCase):
    def test_release_publicado_retorna_metadados_sem_baixar_livros(self):
        with patch.object(mod, "api", side_effect=[
            {"id": 12345, "tag_name": TAG, "draft": False, "prerelease": False},
            [sample_asset()],
        ]) as mocked:
            result = mod.published_assets(TAG)
        self.assertIn("livro.pdf", result)
        self.assertEqual(mocked.call_count, 2)
        self.assertTrue(mod.verify_asset(TAG, result["livro.pdf"], sample_book()))

    def test_hash_alterado_e_reprovado(self):
        with self.assertRaises(ValueError):
            mod.verify_asset(TAG, sample_asset(digest="sha256:" + "b" * 64), sample_book())

    def test_tamanho_errado_e_reprovado(self):
        with self.assertRaises(ValueError):
            mod.verify_asset(TAG, sample_asset(size=122), sample_book())

    def test_asset_sem_digest_exige_verificacao_pelo_cliente(self):
        self.assertFalse(mod.verify_asset(TAG, sample_asset(digest=None), sample_book()))

    def test_tag_invalida_nao_consulta_github(self):
        with patch.object(mod, "api") as mocked:
            with self.assertRaises(ValueError):
                mod.published_assets("../fora")
            mocked.assert_not_called()

    def test_release_rascunho_e_bloqueado(self):
        with patch.object(mod, "api", return_value={
            "id": 123, "tag_name": TAG, "draft": True, "prerelease": False
        }):
            with self.assertRaises(ValueError):
                mod.published_assets(TAG)

    def test_catalogo_inicial_vazio_nao_consulta_github(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "colecoes.json"
            path.write_text(json.dumps({
                "formato": "igetech-workshop-colecoes-v1", "colecoes": []
            }), encoding="utf-8")
            with patch.object(mod, "INDEX", path), patch.object(mod, "api") as mocked:
                self.assertEqual(mod.validate(), 0)
                mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
