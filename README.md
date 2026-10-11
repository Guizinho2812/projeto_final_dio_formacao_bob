# 🚀 DIO Explorer — Projeto Final Formação IBM Bob

> Projeto construído **inteiramente com IBM Bob** em sessão única de chat, como projeto final da Formação IBM Bob na DIO.

---

## 📌 O que é este projeto?

O **DIO Explorer** é uma plataforma completa para explorar trilhas de formação da DIO, gerar desafios de código e emitir certificados de conclusão — tudo integrado ao **IBM Bob** via Slash Commands, Skills e um servidor MCP customizado.

---

## 🗂 Estrutura do Repositório

```
projeto_final_dio_formacao_bob/
├── .bob/
│   ├── commands/               ← Slash commands do Bob
│   │   ├── trilha.md           ← /trilha <tecnologia>
│   │   ├── desafio.md          ← /desafio <tecnologia> [nível]
│   │   └── certificado.md      ← /certificado <nome> <tecnologia>
│   ├── skills/
│   │   ├── trilha/SKILL.md     ← Skill de busca de trilhas
│   │   ├── desafio/SKILL.md    ← Skill de geração de desafios
│   │   └── certificado/SKILL.md← Skill de emissão de certificados
│   └── mcp.json                ← Registro do servidor MCP local
│
├── data/
│   └── trilhas.json            ← 5 trilhas (playground)
│
├── dio_explorer/
│   ├── data/
│   │   └── trilhas_dio.json    ← 15+ formações DIO completas
│   └── mcp/                    ← Servidor MCP TypeScript
│       ├── src/
│       │   ├── index.ts        ← Servidor MCP stdio (Bob local)
│       │   ├── http-server.ts  ← Servidor HTTP/SSE + API REST
│       │   └── data.ts         ← Camada de dados
│       ├── package.json
│       ├── tsconfig.json
│       └── .env.example
│
├── tests/
│   ├── slash_commands_logic.py ← Módulo de lógica testável
│   └── test_slash_commands.py  ← 61 testes unitários (98% cobertura)
│
├── resultado_testes.txt        ← Relatório da suite de testes
├── conftest.py
└── validate_ts.py
```

---

## ✨ Funcionalidades

### 🔷 Slash Commands (IBM Bob)

| Comando | Descrição |
|---|---|
| `/trilha <tecnologia>` | Busca trilha de estudos por tecnologia |
| `/desafio <tecnologia> [nível]` | Gera desafio de código personalizado |
| `/certificado <nome> <tecnologia>` | Emite certificado de conclusão em Markdown |

### 🔷 Skills

Três skills registradas no repositório para uso direto no Bob:
- **trilha** — busca e apresenta plano de estudos
- **desafio** — gera desafio com contexto, requisitos e XP
- **certificado** — emite certificado formatado com data e hash

### 🔷 Servidor MCP TypeScript

5 ferramentas MCP + 2 prompts + API REST completa:

| Ferramenta | Descrição |
|---|---|
| `buscar_trilha` | Busca trilha por tecnologia |
| `listar_trilhas` | Lista todas as formações (filtro por nível) |
| `listar_promocoes` | Retorna formações com promoção ativa |
| `gerar_desafio` | Gera desafio por tecnologia e nível |
| `gerar_certificado` | Gera certificado de conclusão em Markdown |

---

## 🚀 Como usar o Servidor MCP

### Instalação

```bash
cd dio_explorer/mcp
npm install
npm run build
```

### Modo stdio — integração com IBM Bob (local)

Adicione ao `.bob/mcp.json` do workspace:

```json
{
  "mcpServers": {
    "dio-explorer-mcp": {
      "command": "node",
      "args": ["${workspaceFolder}/dio_explorer/mcp/build/index.js"]
    }
  }
}
```

### Modo HTTP/SSE — API REST

```bash
# Padrão (porta 3000)
npm run start:http

# Com porta e API Key personalizadas
PORT=8080 DIO_API_KEY=minha-chave npm run start:http
```

---

## 🌐 API REST — Endpoints

Base URL: `http://localhost:3000`

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/api/trilhas` | Lista todas as trilhas |
| `GET` | `/api/trilhas/:tecnologia` | Busca trilha por tecnologia |
| `GET` | `/api/promocoes` | Lista promoções ativas |
| `POST` | `/api/desafio` | Gera desafio de código |
| `POST` | `/api/certificado` | Emite certificado de conclusão |

### Exemplos

```bash
# Buscar trilha de Java
curl http://localhost:3000/api/trilhas/Java

# Gerar desafio Python Avançado
curl -X POST http://localhost:3000/api/desafio \
  -H "Content-Type: application/json" \
  -d '{"tecnologia":"Python","nivel":"Avançado"}'

# Emitir certificado
curl -X POST http://localhost:3000/api/certificado \
  -H "Content-Type: application/json" \
  -d '{"nome_aluno":"Maria Silva","tecnologia":"React"}'
```

---

## 🧪 Testes

Suite com **61 testes unitários** e **98% de cobertura**:

```bash
# Instalar dependências
pip install pytest pytest-cov

# Rodar todos os testes
pytest tests/ -v

# Com relatório de cobertura
pytest tests/ --cov=tests --cov-report=term-missing
```

Resultado completo disponível em [`resultado_testes.txt`](resultado_testes.txt).

---

## 🔐 Autenticação (API REST)

Se a variável `DIO_API_KEY` estiver definida, todos os endpoints (exceto `/health`) exigem o header:

```
x-api-key: sua-chave-aqui
# ou
Authorization: Bearer sua-chave-aqui
```

---

## 📦 Scripts disponíveis (MCP)

| Comando | Descrição |
|---|---|
| `npm run build` | Compila TypeScript → `build/` |
| `npm run start` | Inicia modo stdio |
| `npm run start:http` | Inicia modo HTTP/SSE + API REST |
| `npm run dev` | Watch mode |
| `npm run clean` | Remove pasta `build/` |

---

## 🤖 Construído com IBM Bob

Este projeto foi desenvolvido **do zero, inteiramente com IBM Bob**, em uma sessão única de chat, como projeto final da **Formação IBM Bob na DIO**.

Todas as etapas foram realizadas pelo Bob:
- Planejamento e arquitetura
- Criação dos slash commands e skills
- Desenvolvimento do servidor MCP em TypeScript
- Implementação da API REST com autenticação
- Escrita dos 61 testes unitários
- Commits e push para o GitHub

---

*Feito com ❤️ e IBM Bob*
