---
description: Exibe o plano de estudos de uma trilha de tecnologia
argument-hint: <tecnologia>
---

O usuário quer visualizar o plano de estudos da trilha de **$1**.

Leia o arquivo `data/trilhas.json` do projeto e localize a trilha cuja propriedade `tecnologia` ou `aliases` corresponda ao valor informado (faça a busca de forma case-insensitive).

Se encontrar a trilha, apresente o plano de estudos formatado assim:

---

# 🗺️ Trilha de [tecnologia]

> [descricao]

**⏱️ Duração estimada:** [duracao_estimada]

---

Para cada módulo, exiba:

## Módulo [numero]: [titulo]
**⏱️ Duração:** [duracao]

| # | Tópico |
|---|--------|
| 1 | [topico 1] |
| 2 | [topico 2] |
...

---

Ao final, exiba uma mensagem motivacional encorajando o usuário a começar a trilha.

Se a tecnologia **não for encontrada** no arquivo, liste as trilhas disponíveis (campo `tecnologia` de cada entrada) e sugira que o usuário escolha uma delas.
