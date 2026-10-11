---
description: Gera um certificado de conclusão de trilha em Markdown
argument-hint: <nome-do-usuario> <trilha>
---

O usuário quer gerar um certificado de conclusão. Os argumentos são: **$1** (nome do usuário) e **$2** (trilha concluída).

Se o nome do usuário **não foi informado** ($1 está vazio), pergunte o nome completo do usuário.
Se a trilha **não foi informada** ($2 está vazio), pergunte qual trilha o usuário concluiu.

Com os dados em mãos, gere o certificado completo em Markdown conforme o modelo abaixo.
Use a data atual do sistema para preencher a data de emissão.

---

Gere exatamente este certificado formatado em Markdown:

```markdown
---

<div align="center">

# 🏆 CERTIFICADO DE CONCLUSÃO

---

## Este certificado é concedido a

# [NOME DO USUÁRIO]

pela conclusão com dedicação e excelência da

## Trilha de [NOME DA TRILHA]

---

### 📚 Conteúdo Concluído

✅ Todos os módulos da trilha foram estudados  
✅ Fundamentos e conceitos avançados dominados  
✅ Projeto final concluído com sucesso  

---

### 📅 Data de Conclusão
**[DATA ATUAL FORMATADA: DD de Mês por extenso de AAAA]**

### 🎓 Emitido por
**Bob — IBM AI Assistant**  
*Plataforma de Aprendizado em Tecnologia*

---

> *"O aprendizado é a única coisa que a mente nunca se cansa,*  
> *nunca tem medo e nunca se arrepende."*  
> — Leonardo da Vinci

---

</div>
```

Após exibir o certificado, adicione uma mensagem de parabéns personalizada e encorajadora para o usuário, mencionando o nome dele e a trilha concluída, e sugira que ele pode agora explorar trilhas mais avançadas ou complementares usando o comando `/trilha`.
