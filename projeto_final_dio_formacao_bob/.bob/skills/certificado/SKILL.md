---
name: certificado
description: Use quando o usuário digitar /certificado para gerar um certificado fictício em Markdown com o nome do usuário e a trilha concluída.
metadata:
  argument-hint: "[seu nome] [nome da trilha]"
---

# /certificado — Gerador de Certificado DIO

## Objetivo
Gerar um certificado fictício e formatado em Markdown para o usuário, com base no seu nome e na trilha concluída. Opcionalmente, salvar o arquivo na pasta `docs/certificados-emitidos/`.

## Passos

### 1. Capturar os argumentos
O usuário pode invocar assim:
- `/certificado João Silva Python`
- `/certificado` (sem argumentos)

Se o **nome do usuário** não for informado, use `ask_followup_question` para solicitá-lo.

Se o **nome da trilha/tecnologia** não for informado, use `ask_followup_question` para perguntar qual trilha foi concluída, sugerindo algumas das disponíveis no `trilhas_dio.json`.

### 2. Buscar dados da trilha
Use `read_file` para ler:
```
projeto_final_dio_formacao_bob/dio_explorer/data/trilhas_dio.json
```
Localize a trilha correspondente (correspondência parcial, case-insensitive) para obter:
- `nome` da formação
- `tecnologia`
- `nivel`
- `modulos`
- `xp_total`
- `badges` (use o último badge da lista como o badge de conclusão)

### 3. Gerar o certificado em Markdown

Produza o certificado no seguinte formato:

```markdown
---

<div align="center">

# 🎓 CERTIFICADO DE CONCLUSÃO

### Digital Innovation One — DIO

---

## ✨ Certificamos que

# <NOME DO USUÁRIO>

concluiu com êxito a formação

## 🏆 <nome da formação>

---

**🛠 Tecnologia:** <tecnologia>
**📊 Nível:** <nivel>
**📦 Módulos Concluídos:** <modulos>
**⭐ XP Conquistado:** <xp_total> XP
**🏅 Badge de Conclusão:** <último badge do array badges>

---

**📅 Data de Emissão:** <data atual no formato DD/MM/AAAA>
**🔑 ID do Certificado:** DIO-<ANO><4 dígitos aleatórios>-<sigla da tecnologia em maiúsculas>

---

> *"A jornada de mil milhas começa com um único passo."*
> Este certificado atesta o compromisso, dedicação e crescimento profissional do(a) aluno(a).

---

🌐 [dio.me](https://www.dio.me) · Plataforma de Educação em Tecnologia

</div>

---
```

Substitua todos os campos `<...>` pelos valores reais obtidos.
- Para o ID do certificado, gere um código único: `DIO-` + ano atual + 4 dígitos aleatórios + `-` + primeiras 3 letras da tecnologia em maiúsculas. Exemplo: `DIO-20250042-PYT`
- Para a data, use a data atual.

### 4. Perguntar sobre salvar o arquivo
Após exibir o certificado no chat, pergunte ao usuário:
> "Deseja salvar este certificado como arquivo `.md` em `docs/certificados-emitidos/`?"

Se o usuário confirmar, use `write_file` para salvar em:
```
projeto_final_dio_formacao_bob/dio_explorer/docs/certificados-emitidos/certificado-<nome-slug>-<trilha-slug>.md
```
Onde o slug é o nome/trilha em lowercase com hífens no lugar de espaços. Inclua o conteúdo Markdown completo do certificado no arquivo.

### 5. Mensagem final
Encerre com uma mensagem de parabenização entusiasmada e personalizada pelo nome do usuário, mencionando a trilha concluída e encorajando os próximos passos na carreira.
