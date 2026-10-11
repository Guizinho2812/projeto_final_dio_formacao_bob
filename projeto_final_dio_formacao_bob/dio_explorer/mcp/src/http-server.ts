/**
 * http-server.ts — DIO Explorer MCP Server com transporte HTTP/SSE
 *
 * Expõe o mesmo servidor MCP via HTTP usando Server-Sent Events (SSE),
 * além de uma API REST JSON para integração direta (sem cliente MCP).
 *
 * Transporte MCP:
 *   GET  /sse          — abre canal SSE para cliente MCP remoto
 *   POST /message      — recebe mensagens MCP do cliente
 *
 * API REST (acesso direto sem cliente MCP):
 *   GET  /api/trilhas                  — lista todas as trilhas
 *   GET  /api/trilhas?nivel=Básico     — filtra por nível
 *   GET  /api/trilhas/:tecnologia      — busca trilha por tecnologia
 *   GET  /api/promocoes                — lista promoções ativas
 *   POST /api/desafio                  — gera desafio { tecnologia, nivel }
 *   POST /api/certificado              — gera certificado { nome_aluno, tecnologia }
 *
 * Autenticação (opcional):
 *   Defina DIO_API_KEY no ambiente para habilitar proteção por header:
 *   x-api-key: <sua-chave>
 *
 * Uso:
 *   npm run start:http
 *   PORT=8080 DIO_API_KEY=secreta npm run start:http
 */

import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { z } from "zod";
import {
  buscarTrilha,
  listarTrilhas,
  listarProducoes,
  formatarTrilha,
  gerarCertificado,
  getTrilhasData,
} from "./data.js";

// ── Configuração ─────────────────────────────────────────────────────────────

const PORT = parseInt(process.env.PORT ?? "3000", 10);
const HOST = process.env.HOST ?? "0.0.0.0";
const API_KEY = process.env.DIO_API_KEY ?? null;
const CORS_ORIGINS = process.env.CORS_ORIGINS ?? "*";

// ── Express App ──────────────────────────────────────────────────────────────

const app = express();

app.use(express.json());
app.use(
  cors({
    origin: CORS_ORIGINS === "*" ? "*" : CORS_ORIGINS.split(","),
    methods: ["GET", "POST", "OPTIONS"],
    allowedHeaders: ["Content-Type", "x-api-key", "Authorization"],
  })
);

// ── Middleware de autenticação ────────────────────────────────────────────────

function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  if (!API_KEY) {
    next();
    return;
  }
  const key = req.headers["x-api-key"] ?? req.headers["authorization"]?.replace("Bearer ", "");
  if (key !== API_KEY) {
    res.status(401).json({ error: "Não autorizado. Forneça um x-api-key válido." });
    return;
  }
  next();
}

// ── Helpers de desafio (replicado do servidor stdio) ─────────────────────────

const DESAFIOS = {
  basico: [
    { titulo: "FizzBuzz Clássico", desc: "Imprima números de 1 a N. Múltiplos de 3 → 'Fizz', de 5 → 'Buzz', ambos → 'FizzBuzz'.", xp: 500, tempo: "30 min" },
    { titulo: "Palíndromo", desc: "Verifique se uma string é um palíndromo, ignorando espaços e capitalização.", xp: 500, tempo: "30 min" },
  ],
  intermediario: [
    { titulo: "Pilha com Mínimo O(1)", desc: "Implemente uma pilha que suporte push, pop e getMin em O(1).", xp: 1200, tempo: "1h" },
    { titulo: "Contagem de Palavras", desc: "Dado um texto, retorne a frequência de cada palavra.", xp: 1200, tempo: "1h" },
  ],
  avancado: [
    { titulo: "Cache LRU", desc: "Implemente LRU Cache com get e put em O(1).", xp: 2500, tempo: "2h" },
    { titulo: "Padrão Observer", desc: "Implemente Observer com múltiplos eventos e desinscrição.", xp: 2500, tempo: "2h" },
  ],
};

type NivelKey = keyof typeof DESAFIOS;

function resolverNivel(nivel: string): NivelKey | null {
  const n = nivel.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z]/g, "");
  const map: Record<string, NivelKey> = {
    basico: "basico",
    intermediario: "intermediario",
    avancado: "avancado",
  };
  return map[n] ?? null;
}

// ── MCP Server (SSE transport) ────────────────────────────────────────────────

const mcpServer = new McpServer({ name: "dio-explorer-mcp", version: "1.0.0" });

mcpServer.registerTool(
  "buscar_trilha",
  {
    description: "Busca uma trilha de formação DIO por tecnologia e retorna o plano de estudos em Markdown.",
    inputSchema: z.object({ tecnologia: z.string() }),
  },
  async ({ tecnologia }) => {
    const trilha = buscarTrilha(tecnologia);
    if (!trilha) {
      return { content: [{ type: "text", text: `❌ Trilha "${tecnologia}" não encontrada.` }], isError: true };
    }
    return { content: [{ type: "text", text: formatarTrilha(trilha) }] };
  }
);

mcpServer.registerTool(
  "listar_trilhas",
  {
    description: "Lista todas as formações disponíveis, com filtro opcional por nível.",
    inputSchema: z.object({ nivel: z.string().optional() }),
  },
  async ({ nivel }) => {
    const trilhas = listarTrilhas(nivel);
    return {
      content: [{ type: "text", text: JSON.stringify(trilhas, null, 2) }],
    };
  }
);

mcpServer.registerTool(
  "gerar_desafio",
  {
    description: "Gera desafio de código por tecnologia e nível.",
    inputSchema: z.object({ tecnologia: z.string(), nivel: z.string() }),
  },
  async ({ tecnologia, nivel }) => {
    const key = resolverNivel(nivel);
    if (!key) return { content: [{ type: "text", text: `❌ Nível inválido: ${nivel}` }], isError: true };
    const opcoes = DESAFIOS[key];
    const d = opcoes[Math.floor(Math.random() * opcoes.length)];
    return { content: [{ type: "text", text: `# ⚔️ Desafio — ${tecnologia} · ${nivel}\n\n**${d.titulo}**\n\n${d.desc}\n\n⭐ ${d.xp} XP · ⏱ ${d.tempo}` }] };
  }
);

mcpServer.registerTool(
  "gerar_certificado",
  {
    description: "Gera certificado de conclusão em Markdown.",
    inputSchema: z.object({ nome_aluno: z.string(), tecnologia: z.string() }),
  },
  async ({ nome_aluno, tecnologia }) => ({
    content: [{ type: "text", text: gerarCertificado(nome_aluno, tecnologia) }],
  })
);

// ── Rotas SSE (transporte MCP remoto) ────────────────────────────────────────

const sseTransports: Map<string, SSEServerTransport> = new Map();

app.get("/sse", authMiddleware, async (req: Request, res: Response) => {
  console.error(`[SSE] Nova conexão de ${req.ip}`);
  const transport = new SSEServerTransport("/message", res);
  sseTransports.set(transport.sessionId, transport);

  res.on("close", () => {
    sseTransports.delete(transport.sessionId);
    console.error(`[SSE] Conexão encerrada: ${transport.sessionId}`);
  });

  await mcpServer.connect(transport);
});

app.post("/message", authMiddleware, async (req: Request, res: Response) => {
  const sessionId = req.query["sessionId"] as string;
  const transport = sseTransports.get(sessionId);
  if (!transport) {
    res.status(404).json({ error: "Sessão não encontrada." });
    return;
  }
  await transport.handlePostMessage(req, res);
});

// ── API REST ─────────────────────────────────────────────────────────────────

/**
 * GET /api/trilhas
 * GET /api/trilhas?nivel=Intermediário
 */
app.get("/api/trilhas", authMiddleware, (req: Request, res: Response) => {
  const nivel = req.query["nivel"] as string | undefined;
  const trilhas = listarTrilhas(nivel);
  res.json({ total: trilhas.length, trilhas });
});

/**
 * GET /api/trilhas/:tecnologia
 */
app.get("/api/trilhas/:tecnologia", authMiddleware, (req: Request, res: Response) => {
  const { tecnologia } = req.params;
  const trilha = buscarTrilha(tecnologia);
  if (!trilha) {
    const disponiveis = getTrilhasData().trilhas.map((t) => t.tecnologia);
    res.status(404).json({ error: `Trilha "${tecnologia}" não encontrada.`, disponiveis });
    return;
  }
  res.json(trilha);
});

/**
 * GET /api/promocoes
 */
app.get("/api/promocoes", authMiddleware, (req: Request, res: Response) => {
  const promos = listarProducoes();
  res.json({ total: promos.length, promocoes: promos });
});

/**
 * POST /api/desafio
 * Body: { "tecnologia": "Java", "nivel": "Intermediário" }
 */
app.post("/api/desafio", authMiddleware, (req: Request, res: Response) => {
  const schema = z.object({
    tecnologia: z.string().min(1),
    nivel: z.string().min(1),
  });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Parâmetros inválidos.", detalhes: parsed.error.flatten() });
    return;
  }
  const { tecnologia, nivel } = parsed.data;
  const key = resolverNivel(nivel);
  if (!key) {
    res.status(400).json({ error: `Nível "${nivel}" inválido. Use: Básico, Intermediário ou Avançado.` });
    return;
  }
  const opcoes = DESAFIOS[key];
  const desafio = opcoes[Math.floor(Math.random() * opcoes.length)];
  res.json({ tecnologia, nivel, ...desafio });
});

/**
 * POST /api/certificado
 * Body: { "nome_aluno": "Carlos Alves", "tecnologia": "Java" }
 */
app.post("/api/certificado", authMiddleware, (req: Request, res: Response) => {
  const schema = z.object({
    nome_aluno: z.string().min(1),
    tecnologia: z.string().min(1),
  });
  const parsed = schema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Parâmetros inválidos.", detalhes: parsed.error.flatten() });
    return;
  }
  const { nome_aluno, tecnologia } = parsed.data;
  const markdown = gerarCertificado(nome_aluno, tecnologia);
  res.json({ nome_aluno, tecnologia, certificado_markdown: markdown });
});

// ── Health check ─────────────────────────────────────────────────────────────

app.get("/health", (_req: Request, res: Response) => {
  res.json({
    status: "ok",
    servidor: "dio-explorer-mcp",
    versao: "1.0.0",
    autenticacao: API_KEY ? "api-key" : "nenhuma",
    transportes: ["HTTP/SSE (/sse)", "API REST (/api/*)"],
    trilhas_carregadas: getTrilhasData().trilhas.length,
    timestamp: new Date().toISOString(),
  });
});

// ── Root info ─────────────────────────────────────────────────────────────────

app.get("/", (_req: Request, res: Response) => {
  res.json({
    nome: "DIO Explorer MCP Server",
    versao: "1.0.0",
    descricao: "MCP Server para trilhas, desafios e certificados DIO",
    endpoints: {
      mcp_sse: "GET /sse",
      mcp_message: "POST /message?sessionId=<id>",
      api_trilhas: "GET /api/trilhas[?nivel=...]",
      api_trilha: "GET /api/trilhas/:tecnologia",
      api_promocoes: "GET /api/promocoes",
      api_desafio: "POST /api/desafio",
      api_certificado: "POST /api/certificado",
      health: "GET /health",
    },
    docs: "Consulte o README.md na pasta mcp/ para mais detalhes.",
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────

app.listen(PORT, HOST, () => {
  console.error(`✅ DIO Explorer MCP HTTP Server rodando em http://${HOST}:${PORT}`);
  console.error(`   Autenticação: ${API_KEY ? "✅ api-key ativa" : "⚠️  nenhuma (apenas dev)"}`);
  console.error(`   MCP SSE:  http://${HOST}:${PORT}/sse`);
  console.error(`   API REST: http://${HOST}:${PORT}/api/trilhas`);
  console.error(`   Health:   http://${HOST}:${PORT}/health`);
});
