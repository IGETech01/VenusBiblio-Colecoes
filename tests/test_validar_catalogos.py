"""Testes offline de estrutura e privacidade do repositório público."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validar_catalogos.py"
SHA_TESTE = hashlib.sha256(b"%PDF-1.7\n%%EOF\n").hexdigest()


class ValidacaoPublicaTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="vb_repo_test_")
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / "workshop").mkdir()
        shutil.copy2(SOURCE_SCRIPT, self.root / "scripts" / "validar_catalogos.py")
        (self.root / "README.md").write_text("# Catálogo público de testes\n", encoding="utf-8")
        self.indice([])

    def tearDown(self):
        self.temp.cleanup()

    def indice(self, colecoes):
        doc = {"formato": "igetech-workshop-colecoes-v1", "colecoes": colecoes}
        (self.root / "workshop" / "colecoes.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8"
        )

    def catalogo(self, *, repo="IGETech01/VenusBiblio-Colecoes", ids=("livro1",), kind="Livro"):
        pasta = self.root / "workshop" / "colecoes" / "classicos"
        pasta.mkdir(parents=True, exist_ok=True)
        livros = []
        for ident in ids:
            livros.append({
                "id": ident, "titulo": "Obra de teste", "autor": "Autor",
                "genero": "Literatura", "licenca": "CC0-1.0",
                "arquivo": f"livros/{ident}.pdf", "sha256": SHA_TESTE,
                "tamanho": 15, "tipo_conteudo": kind
            })
        doc = {
            "formato": "biblioteca-offline-workshop-v1",
            "nome": "Clássicos", "descricao": "Livros autorizados",
            "distribuicao": {
                "tipo": "github_release", "repositorio": repo,
                "tag": "colecao-classicos-v1"
            }, "livros": livros
        }
        (pasta / "catalogo.json").write_text(
            json.dumps(doc, ensure_ascii=False), encoding="utf-8"
        )
        self.indice([{
            "id": "classicos", "nome": "Clássicos",
            "descricao": "Livros autorizados", "quantidade": len(livros)
        }])
        return pasta

    def run_validation(self, success):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts" / "validar_catalogos.py")],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_indice_inicial_vazio_e_valido(self):
        self.run_validation(True)

    def test_colecao_real_com_um_livro_e_valida(self):
        self.catalogo()
        self.run_validation(True)

    def test_catalogo_inexistente_falha(self):
        pasta = self.catalogo()
        (pasta / "catalogo.json").unlink()
        self.run_validation(False)

    def test_repositorio_externo_e_bloqueado(self):
        self.catalogo(repo="OutraPessoa/OutroRepo")
        self.run_validation(False)

    def test_ids_repetidos_ignorando_maiusculas_sao_bloqueados(self):
        self.catalogo(ids=("Livro1", "livro1"))
        self.run_validation(False)

    def test_json_com_chave_duplicada_e_bloqueado(self):
        (self.root / "workshop" / "colecoes.json").write_text(
            '{"formato":"igetech-workshop-colecoes-v1","colecoes":[],"colecoes":[]}',
            encoding="utf-8"
        )
        self.run_validation(False)

    def test_arquivo_de_backup_na_raiz_e_bloqueado(self):
        (self.root / ".env").write_text("NAO_PUBLICAR=sim", encoding="utf-8")
        self.run_validation(False)

    def test_documento_interno_nao_permitido_e_bloqueado(self):
        (self.root / "INSTRUCOES_PRIVADAS.txt").write_text("privado", encoding="utf-8")
        self.run_validation(False)

    def test_arquivo_inesperado_dentro_da_colecao_e_bloqueado(self):
        pasta = self.catalogo()
        (pasta / "secret.txt").write_text("privado", encoding="utf-8")
        self.run_validation(False)

    def test_token_simulado_em_arquivo_permitido_e_bloqueado(self):
        (self.root / "README.md").write_text(
            "Token fictício github_pat_" + ("X" * 32), encoding="utf-8"
        )
        self.run_validation(False)

    def test_obras_sem_hash_valido_sao_bloqueadas(self):
        pasta = self.catalogo()
        f = pasta / "catalogo.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        doc["livros"][0]["sha256"] = "invalido"
        f.write_text(json.dumps(doc), encoding="utf-8")
        self.run_validation(False)

    def test_colecao_nao_indexada_e_bloqueada(self):
        self.catalogo()
        self.indice([])
        self.run_validation(False)


if __name__ == "__main__":
    unittest.main()
