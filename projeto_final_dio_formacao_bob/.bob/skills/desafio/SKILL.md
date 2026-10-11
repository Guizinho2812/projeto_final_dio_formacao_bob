---
name: desafio
description: Use quando o usuário digitar /desafio para gerar um desafio de código aleatório baseado em uma tecnologia e nível escolhidos.
metadata:
  argument-hint: "[tecnologia] [nivel]"
---

# /desafio — Gerador de Desafio de Código DIO

## Objetivo
Gerar um desafio de código aleatório, único e contextualizado com base na tecnologia e nível informados pelo usuário.

## Passos

### 1. Capturar os argumentos
O usuário pode invocar de diferentes formas:
- `/desafio Python Básico`
- `/desafio` (sem argumentos)

Se a tecnologia **não** for informada, use `ask_followup_question` com sugestões:
- "Python"
- "JavaScript"
- "Java"
- "Go"
- (outras tecnologias presentes no `trilhas_dio.json`)

Se o nível **não** for informado, use `ask_followup_question` com as opções:
- "Básico"
- "Intermediário"
- "Avançado"

### 2. Sortear o tipo de desafio
Escolha **aleatoriamente** um dos seguintes tipos de desafio conforme o nível:

**Básico:**
- Algoritmo simples (ex: FizzBuzz, palíndromo, fatorial)
- Manipulação de strings
- Operações com arrays/listas

**Intermediário:**
- Estruturas de dados (pilha, fila, lista ligada)
- Algoritmos de ordenação
- Consumo de API REST com tratamento de erro
- CRUD simples com banco de dados

**Avançado:**
- Design patterns (Factory, Observer, Strategy)
- Programação concorrente / assíncrona
- Otimização de performance
- Implementação de um mini-framework ou biblioteca
- Arquitetura de microsserviços (diagrama + código)

### 3. Gerar o desafio

Produza o desafio completo no seguinte formato Markdown:

```
# ⚔️ Desafio DIO — <tecnologia> · <nivel>

**🎯 Tipo:** <tipo do desafio sorteado>
**⏱ Tempo estimado:** <tempo realista baseado no nível: Básico=30min, Intermediário=1h, Avançado=2h>
**⭐ XP ao concluir:** <xp: Básico=500, Intermediário=1200, Avançado=2500>

---

## 📋 Descrição
<Descreva o problema de forma clara e contextualizada, como se fosse um enunciado real de plataforma de desafios.
Use 3-5 parágrafos. Inclua o contexto do mundo real onde esse problema se aplica.>

---

## 📥 Entrada
<Descreva o formato da entrada esperada, com exemplos concretos de valores.>

## 📤 Saída Esperada
<Descreva a saída esperada para os exemplos de entrada.>

---

## 💡 Dica
<Forneça uma dica útil sem entregar a solução. Mencione conceitos ou funções nativas relevantes.>

---

## ✅ Critérios de Aceite
Liste de 3 a 5 critérios objetivos que a solução deve atender para ser considerada correta.

---

## 🧪 Casos de Teste
Forneça pelo menos 3 casos de teste em formato de tabela:

| Entrada | Saída Esperada |
|---------|----------------|
| ...     | ...            |
```

### 4. Entregar no chat
Renderize o desafio diretamente no chat em Markdown. Não salve em arquivo. Ao final, pergunte se o usuário quer ver a **solução comentada** ou tentar primeiro por conta própria.
