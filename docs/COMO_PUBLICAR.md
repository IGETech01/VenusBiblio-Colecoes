# Publicação de coleções para o Workshop VenusBiblio

O Workshop lê o índice público `workshop/colecoes.json` na branch `main`.
Os catálogos ficam em `workshop/colecoes/ID/catalogo.json` e as capas em
`workshop/colecoes/ID/capas/`.

**Os PDFs, EPUBs e CBZs ficam nos anexos de um GitHub Release, não nos commits.**

## Passos

1. No **Workshop Admin** de uma conta desenvolvedora autorizada, exporte uma coleção
   local e use **Preparar publicação no GitHub**. Confirme previamente que todas
   as obras podem ser redistribuídas.
2. A ferramenta gera `ASSETS_DO_RELEASE/`, `ARQUIVOS_DO_REPOSITORIO/`
   e instruções. Revise todos os arquivos e as permissões de publicação.
3. Crie no GitHub um Release de coleção com a tag indicada pela ferramenta,
   por exemplo `colecao-classicos-v1`, anexando **todos os livros** de
   `ASSETS_DO_RELEASE/`. Não marque como versão mais recente do aplicativo.
4. Envie `workshop/colecoes/ID/catalogo.json` e as capas geradas para a branch
   `main` **sem alterar os nomes**. Confira o SHA-256 e o tamanho de cada livro.
5. Mescle a entrada nova de `colecoes.json` ao índice já publicado. **Não substitua
   o índice inteiro**, senão outras coleções poderão desaparecer.
6. Execute `python scripts/validar_catalogos.py` antes do commit. O workflow do
   GitHub também verificará a estrutura quando houver alterações.
7. No VenusBiblio, abra **Workshop → Coleções públicas**. Verifique a descoberta,
   baixe uma obra autorizada e confirme que ela abre offline.

## Regras de segurança

- Somente PDFs, EPUBs e CBZs com licença adequada. O app exige SHA-256
  de 64 caracteres e arquivos de até **250 MiB cada**.
- Use nomes de assets simples, sem espaços nem caminhos relativos complexos.
- Use tags `colecao-ID-vN` e mantenha o repositório de distribuição
  `IGETech01/VenusBiblio-Colecoes`.
- Use `catalogo.json` com `formato: biblioteca-offline-workshop-v1`,
  `distribuicao.tipo: github_release`, `distribuicao.repositorio` e
  `distribuicao.tag` compatíveis com o preparador da versão 0.14.9-dev.
- Não publique arquivos privados, contas, certificados, dados pessoais,
  backups, chaves, livros não autorizados ou informações do servidor local.
- É conteúdo **público**: quem tiver o link poderá baixar os arquivos.
  GitHub Releases não é um controle de acesso para conteúdo pago.

## Disponibilidade

A leitura de catálogo requer internet. Depois de importar os livros,
a leitura da cópia local funciona offline. O GitHub pode aplicar limites
de disponibilidade e transferência; não é um serviço com SLA contratado.

## Exemplo (apenas documentação)

[`docs/EXEMPLO_CATALOGO.json`](EXEMPLO_CATALOGO.json) ilustra a estrutura de um
catálogo vazio. **Não o adicione ao índice** nem publique uma coleção vazia.
