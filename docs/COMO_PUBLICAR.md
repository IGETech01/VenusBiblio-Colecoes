# Publicar coleções do Workshop VenusBiblio

Este repositório hospeda **coleções de livros**, não o instalador do programa. O download do VenusBiblio é feito na [página oficial IGETech](https://igetech01.github.io/VenusBiblio-Updates/).

## Estrutura compatível com o VenusBiblio

O aplicativo consulta o arquivo `workshop/colecoes.json` na branch `main`. Cada entrada com ID `classicos`, por exemplo, aponta para `workshop/colecoes/classicos/catalogo.json`. As capas ficam em `workshop/colecoes/classicos/capas/`.

**Os livros PDF, EPUB e CBZ devem ser anexados a GitHub Releases desta mesma conta e repositório; não devem ser adicionados aos commits.**

## Processo de publicação

1. No Workshop Admin, com conta de desenvolvedor autorizada, exporte a coleção e use **Preparar publicação no GitHub**. Confira os direitos de redistribuição de cada obra.
2. A ferramenta prepara `ASSETS_DO_RELEASE/`, `ARQUIVOS_DO_REPOSITORIO/` e instruções. Revise o conteúdo para garantir que não haja dados pessoais, segredos ou material não autorizado.
3. Crie um Release com a tag exata gerada, por exemplo `colecao-classicos-v1`, e anexe todos os livros preparados, mantendo os nomes. Se publicar outra edição da coleção, use uma nova tag.
4. Somente depois de os arquivos do Release estarem disponíveis, publique `workshop/colecoes/ID/catalogo.json` e suas capas na branch `main`.
5. **Mescle** a entrada da nova coleção em `workshop/colecoes.json`; nunca substitua o índice inteiro, pois isso apagaria outras coleções da lista.
6. Execute `python scripts/validar_catalogos.py` antes do commit. O GitHub Actions também examinará a estrutura ao receber alterações.
7. Teste no VenusBiblio: abra **Workshop → Coleções públicas**, descubra a coleção, baixe um livro autorizado e confirme a leitura offline.

## Formatos e integridade

- O índice usa o formato `igetech-workshop-colecoes-v1`.
- Cada catálogo usa o formato `biblioteca-offline-workshop-v1` e o campo `distribuicao` com `tipo: github_release`, `repositorio: IGETech01/VenusBiblio-Colecoes` e `tag: colecao-ID-vN`.
- Os arquivos de cada livro ficam declarados no catálogo como `livros/NOME.pdf`, `livros/NOME.epub` ou `livros/NOME.cbz`, com `sha256` e `tamanho` reais. Cada livro pode ter no máximo **250 MiB**.
- As capas ficam em `capas/NOME.png` (ou JPG/WEBP) e têm limite de **2 MiB**.
- Os nomes de arquivos e IDs precisam respeitar os formatos aceitos pelo preparador, sem caminhos absolutos, `..`, URL ou nomes de arquivos arbitrários.
- Arquivos de Release são públicos; **não use GitHub Releases como mecanismo de autenticação, conteúdo privado ou assinatura paga**.

## Cuidados operacionais

O GitHub é usado como hospedagem estática; ele pode aplicar limites de disponibilidade ou transferência. A leitura dos livros já importados continua offline mesmo se o catálogo estiver temporariamente indisponível.

**A primeira coleção ainda não foi publicada.** O arquivo [EXEMPLO_CATALOGO.json](EXEMPLO_CATALOGO.json) é apenas documentação e não deve ser colocado no índice enquanto estiver vazio.
