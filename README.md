# VenusBiblio · Coleções públicas IGETech

Este repositório é a **infraestrutura de distribuição das coleções do Workshop**. Ele não é a página inicial nem o canal de instalação do VenusBiblio.

## 📥 Onde baixar o programa?

**Acesse a [página oficial de downloads do VenusBiblio](https://igetech01.github.io/VenusBiblio-Updates/).**

Esse é o endereço público destinado aos usuários. O repositório `VenusBiblio-Updates` fornece os instaladores por trás daquela página; este repositório, `VenusBiblio-Colecoes`, fornece **somente catálogos e livros**.

## 📚 Workshop: coleções de qualquer lugar

O VenusBiblio consulta o [índice oficial de coleções](workshop/colecoes.json), abre os catálogos públicos e permite baixar livros autorizados com verificação de tamanho e SHA-256. Após o download, a leitura é offline.

**Estado atual: nenhuma coleção publicada.** O índice inicial está vazio por segurança. Nenhum servidor privado da IGE é necessário para consultar este catálogo.

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
