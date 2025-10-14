Este projeto utiliza **submódulos Git** para incluir outros repositórios como dependências internas.  

---

## Clonando o repositório (com submódulos)

Ao clonar este repositório, use a flag `--recurse-submodules` para baixar também os submódulos automaticamente:

```bash

git clone --recurse-submodules git@github.com:henriquefac/vector_rag.git

```

Se já clonou o repositório sem os submódulos:

```bash
git submodule update --init --recursive

```

Atualizando submódulos

```bash
git submodule update --remote --merge

```
