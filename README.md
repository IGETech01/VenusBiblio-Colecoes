# VenusBiblio · Coleções públicas IGETech

Este espaço reúne as coleções disponíveis no **Workshop Cliente do VenusBiblio**. Para conhecer ou instalar o programa, use a página oficial.

## 📥 Onde baixar o programa?

**[Baixar VenusBiblio para Windows](https://igetech01.github.io/VenusBiblio-Updates/baixar/)** · [Conhecer o programa](https://igetech01.github.io/VenusBiblio-Updates/demo/)

As coleções podem ser consultadas dentro do VenusBiblio. Esta página é dedicada aos catálogos, não ao instalador.

## 📚 Workshop: coleções de qualquer lugar

Explore as coleções disponíveis pelo Workshop Cliente. Depois de baixar os arquivos, você pode ler offline.

**Coleções disponíveis:** consulte o [catálogo atualizado](workshop/colecoes.json).

## Estrutura do serviço

- `workshop/colecoes.json`: índice de descoberta compatível com o cliente.
- `workshop/colecoes/ID/catalogo.json`: metadados de uma coleção publicada.
- `workshop/colecoes/ID/capas/`: capas e imagens do catálogo.
- **GitHub Releases deste repositório**: anexos PDF, EPUB ou CBZ de cada coleção.

Para preparar e publicar uma coleção, leia o [guia de publicação](docs/COMO_PUBLICAR.md). As notas do arquivo de exemplo em `docs/` são apenas ilustrativas e não constituem uma coleção publicada.

## Segurança e direitos de distribuição

Publique apenas obras em domínio público ou com **licença/autorização que permita redistribuição**. Todo conteúdo deste repositório e de seus Releases é público e pode ser acessado sem login.

O repositório não deve conter bancos de dados de contas, chaves, credenciais, arquivos de configuração privados, ferramentas administrativas ou código-fonte proprietário. A [validação automática](.github/workflows/validar-catalogos.yml) examina os arquivos permitidos e a estrutura dos catálogos. Os hashes das obras são conferidos pelo cliente durante o download.

**Portal oficial do programa:** https://igetech01.github.io/VenusBiblio-Updates/
