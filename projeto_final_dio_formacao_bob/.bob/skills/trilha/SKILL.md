---
name: trilha
description: Use quando o usuário digitar /trilha seguido do nome de uma tecnologia para exibir o plano de estudos formatado daquela trilha a partir do arquivo data/trilhas_dio.json.
metadata:
  argument-hint: "[nome da tecnologia]"
---

# /trilha — Plano de Estudos da Formação DIO

## Objetivo
Buscar a trilha correspondente à tecnologia informada pelo usuário no arquivo `trilhas_dio.json` e exibir um plano de estudos completo e formatado.

## Passos

### 1. Capturar o argumento
O usuário invoca o comando assim:
```
/trilha <tecnologia>
```
Extraia o nome da tecnologia informado. Se nenhum argumento for passado, use `ask_followup_question` para perguntar qual tecnologia o usuário deseja buscar.

### 2. Ler o arquivo de trilhas
Use `read_file` para ler o arquivo localizado em:
```
projeto_final_dio_formacao_bob/dio_explorer/data/trilhas_dio.json
```

### 3. Buscar a trilha
Percorra o array `trilhas` do JSON e encontre a entrada cujo campo `tecnologia` ou `nome` contenha (correspondência parcial, case-insensitive) o argumento fornecido.

- Se **nenhuma trilha** for encontrada, informe o usuário e liste os nomes de todas as trilhas disponíveis no arquivo para que ele possa escolher.
- Se **mais de uma trilha** corresponder, liste as opções e peça ao usuário que especifique melhor.

### 4. Formatar o plano de estudos

Com os dados da trilha encontrada, gere a seguinte saída em Markdown:

```
# 🎓 Formação DIO — <nome>

**🛠 Tecnologia:** <tecnologia>
**📊 Nível:** <nivel>
**📦 Módulos:** <modulos>
**⭐ XP Total:** <xp_total> XP
**♾️ Acesso Vitalício:** Sim / Não

---

## 📚 Plano de Estudos

Gere uma lista numerada com <modulos> módulos fictícios e realistas para a tecnologia da trilha.
Cada módulo deve ter um nome descritivo, uma breve descrição de 1 linha e uma estimativa de duração.

Exemplo de formato por módulo:
**Módulo 1 — Fundamentos de <tecnologia>**
> Introdução aos conceitos base, instalação do ambiente e primeiros passos.
> ⏱ Estimativa: 4h

---

## 🏅 Badges Disponíveis
Liste cada badge do array `badges` com um emoji de medalha antes do nome.

---

## 🎁 Promoção
Se `promocao.ativa` for true:
  - Exiba: "🔥 **<desconto_percentual>% OFF** — Válido até <validade>"
Se false:
  - Exiba: "Sem promoção ativa no momento."

---

## 📡 Lives ao Vivo
Liste cada live do array `lives_ao_vivo` com:
- 🔴 **<titulo>** — <data> · <duracao_min> min
```

### 5. Entregar a resposta
Renderize o plano de estudos diretamente no chat em Markdown. Não use ferramentas de arquivo para salvar a saída — apenas exiba no chat.
