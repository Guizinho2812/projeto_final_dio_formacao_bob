# DIO Explorer MCP Server

Servidor MCP para o projeto **DIO Explorer** — expõe trilhas de formação, gerador de desafios e emissor de certificados como ferramentas MCP consumíveis pelo IBM Bob (e qualquer cliente MCP compatível).

---

## 🗂 Estrutura

```
mcp/
├── src/
│   ├── index.ts        ← Servidor MCP via stdio (uso com Bob)
│   ├── http-server.ts  ← Servidor MCP via HTTP/SSE + API REST
│   └── data.ts         ← Camada de dados (lê trilhas_dio.json)
├── build/              ← Saída compilada (gerada por npm run build)
├── package.json
├── tsconfig.json
├── .env.example        ← Variáveis de ambiente disponíveis
└── README.md
```

---

## 🚀 Instalação

```bash
cd projeto_final_dio_formacao_bob/dio_explorer/mcp
npm install
npm run build
```

---

## 🔧 Modos de uso

### 1. Modo stdio — integração com IBM Bob (local)

O servidor é iniciado automaticamente pelo Bob como processo filho.
Não requer porta ou rede. Registre no `mcp.json` do workspace (veja abaixo).

```bash
# Teste manual no terminal
node build/index.js
```

### 2. Modo HTTP/SSE — acesso remoto / API

```bash
# Padrão (porta 3000, sem autenticação)
npm run start:http

# Com porta e API Key personalizadas
PORT=8080 DIO_API_KEY=minha-chave npm run start:http
```

---

## 🛠 Ferramentas MCP disponíveis

| Ferramenta | Descrição |
|---|---|
| `buscar_trilha` | Busca trilha por tecnologia e retorna plano de estudos em Markdown |
| `listar_trilhas` | Lista todas as formações (filtro opcional por nível) |
| `listar_promocoes` | Retorna formações com promoção ativa |
| `gerar_desafio` | Gera desafio de código por tecnologia e nível |
| `gerar_certificado` | Gera certificado de conclusão em Markdown |

### Prompts MCP

| Prompt | Descrição |
|---|---|
| `trilha_prompt` | Template para explorar uma trilha e montar plano de 3 meses |
| `desafio_prompt` | Template para receber desafio e ver solução passo a passo |

---

## 🌐 API REST (modo HTTP)

Base URL: `http://localhost:3000`

### `GET /`
Retorna informações do servidor e lista de endpoints.

### `GET /health`
Health check — retorna status, versão, número de trilhas carregadas.

### `GET /api/trilhas`
Lista todas as trilhas.

**Query params:**
- `nivel` — filtra por nível (`Básico`, `Intermediário`, `Avançado`)

**Exemplos:**
```bash
curl http://localhost:3000/api/trilhas
curl http://localhost:3000/api/trilhas?nivel=Intermediário
```

### `GET /api/trilhas/:tecnologia`
Busca trilha por tecnologia (busca parcial, case-insensitive).

```bash
curl http://localhost:3000/api/trilhas/Java
curl http://localhost:3000/api/trilhas/python
```

### `GET /api/promocoes`
Lista formações com promoção ativa.

```bash
curl http://localhost:3000/api/promocoes
```

### `POST /api/desafio`
Gera um desafio de código aleatório.

**Body JSON:**
```json
{ "tecnologia": "Java", "nivel": "Intermediário" }
```

```bash
curl -X POST http://localhost:3000/api/desafio \
  -H "Content-Type: application/json" \
  -d '{"tecnologia":"Java","nivel":"Intermediário"}'
```

### `POST /api/certificado`
Gera um certificado de conclusão em Markdown.

**Body JSON:**
```json
{ "nome_aluno": "Carlos Alves", "tecnologia": "Java" }
```

```bash
curl -X POST http://localhost:3000/api/certificado \
  -H "Content-Type: application/json" \
  -d '{"nome_aluno":"Carlos Alves","tecnologia":"Java"}'
```

---

## 🔐 Autenticação

Se a variável `DIO_API_KEY` estiver definida, todos os endpoints (exceto `/health`) exigem:

```
x-api-key: sua-chave-aqui
# ou
Authorization: Bearer sua-chave-aqui
```

**Exemplo:**
```bash
curl http://localhost:3000/api/trilhas \
  -H "x-api-key: minha-chave-secreta"
```

---

## 🔌 Transporte MCP via SSE (clientes remotos)

Para conectar um cliente MCP ao servidor HTTP:

```
SSE endpoint: GET  http://localhost:3000/sse
Message:      POST http://localhost:3000/message?sessionId=<id>
```

**Configuração em `mcp.json` (cliente remoto):**
```json
{
  "mcpServers": {
    "dio-explorer-mcp": {
      "url": "http://localhost:3000/sse",
      "headers": {
        "x-api-key": "${env:DIO_API_KEY}"
      }
    }
  }
}
```

---

## 📋 Registro no Bob (stdio — uso local)

Adicione ao arquivo `.bob/mcp.json` do workspace:

```json
{
  "mcpServers": {
    "dio-explorer-mcp": {
      "command": "node",
      "args": ["${workspaceFolder}/projeto_final_dio_formacao_bob/dio_explorer/mcp/build/index.js"]
    }
  }
}
```

---

## 🔄 Níveis aceitos pelo `gerar_desafio`

| Valor aceito | Normalizado | XP | Tempo |
|---|---|---|---|
| `Básico`, `Basico`, `basico` | Básico | 500 XP | 30 min |
| `Intermediário`, `Intermediario` | Intermediário | 1200 XP | 1h |
| `Avançado`, `Avancado`, `avancado` | Avançado | 2500 XP | 2h |

---

## 🧪 Testando localmente

```bash
# Health check
curl http://localhost:3000/health

# Buscar Java
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

## 📦 Scripts disponíveis

| Comando | Descrição |
|---|---|
| `npm run build` | Compila TypeScript → `build/` |
| `npm run start` | Inicia modo stdio |
| `npm run start:http` | Inicia modo HTTP/SSE + API REST |
| `npm run dev` | Watch mode (recompila ao salvar) |
| `npm run clean` | Remove pasta `build/` |
