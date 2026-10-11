#!/usr/bin/env node
/**
 * index.ts — DIO Explorer MCP Server (transporte stdio)
 *
 * Expõe as seguintes ferramentas ao Bob / qualquer cliente MCP:
 *
 *   buscar_trilha       — busca uma trilha por tecnologia e retorna plano de estudos
 *   listar_trilhas      — lista todas as trilhas (com filtro opcional de nível)
 *   listar_promocoes    — retorna trilhas com promoção ativa
 *   gerar_desafio       — gera um desafio de código para uma tecnologia e nível
 *   gerar_certificado   — gera um certificado de conclusão em Markdown
 *
 * Prompts registrados:
 *   trilha_prompt       — template de prompt para explorar uma trilha
 *   desafio_prompt      — template de prompt para gerar um desafio
 *
 * Transporte: stdio (uso local / Bob IDE)
 * Para acesso HTTP/SSE/API REST, use: npm run start:http
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import {
  buscarTrilha,
  listarTrilhas,
  listarProducoes,
  formatarTrilha,
  gerarCertificado,
  getTrilhasData,
} from "./data.js";

// ── Desafios por nível ───────────────────────────────────────────────────────

const DESAFIOS = {
  basico: [
    { titulo: "FizzBuzz Clássico", desc: "Imprima números de 1 a N. Múltiplos de 3 → 'Fizz', de 5 → 'Buzz', ambos → 'FizzBuzz'.", xp: 500, tempo: "30 min" },
    { titulo: "Palíndromo", desc: "Verifique se uma string é um palíndromo (lê igual de frente para trás), ignorando espaços e capitalização.", xp: 500, tempo: "30 min" },
    { titulo: "Fatorial Recursivo", desc: "Calcule o fatorial de N usando recursão. Trate N=0 e entradas negativas.", xp: 500, tempo: "30 min" },
  ],
  intermediario: [
    { titulo: "Pilha com Mínimo O(1)", desc: "Implemente uma pilha que suporte push, pop e getMin em tempo constante.", xp: 1200, tempo: "1h" },
    { titulo: "Contagem de Palavras", desc: "Dado um texto, retorne um mapa com a frequência de cada palavra, ignorando pontuação e case.", xp: 1200, tempo: "1h" },
    { titulo: "Consumo de API REST", desc: "Consuma a API JSONPlaceholder e exiba os títulos dos 5 primeiros posts em ordem alfabética.", xp: 1200, tempo: "1h" },
  ],
  avancado: [
    { titulo: "Cache LRU", desc: "Implemente um cache Least Recently Used com capacidade configurável. get e put em O(1).", xp: 2500, tempo: "2h" },
    { titulo: "Padrão Observer", desc: "Implemente o padrão Observer com suporte a múltiplos eventos, prioridades e desinscrição.", xp: 2500, tempo: "2h" },
    { titulo: "Pool de Threads", desc: "Crie um pool de workers com fila de tarefas, limite de concorrência e cancelamento.", xp: 2500, tempo: "2h" },
  ],
};

function sortearDesafio(nivel: string, tecnologia: string): string {
  const nivelKey = nivel.toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z]/g, "") as keyof typeof DESAFIOS;

  const map: Record<string, keyof typeof DESAFIOS> = {
    basico: "basico",
    intermediario: "intermediario",
    avancado: "avancado",
  };
  const key = map[nivelKey];
  if (!key) {
    return `❌ Nível inválido: "${nivel}". Use Básico, Intermediário ou Avançado.`;
  }

  const opcoes = DESAFIOS[key];
  const desafio = opcoes[Math.floor(Math.random() * opcoes.length)];

  return [
    `# ⚔️ Desafio DIO — ${tecnologia} · ${nivel}`,
    "",
    `**🎯 Tipo:** ${desafio.titulo}`,
    `**⏱ Tempo estimado:** ${desafio.tempo}`,
    `**⭐ XP ao concluir:** ${desafio.xp} XP`,
    "",
    "---",
    "",
    "## 📋 Descrição",
    desafio.desc,
    "",
    "## 💡 Dica",
    "Pesquise sobre a estrutura de dados ou padrão mais adequado antes de codificar.",
    "",
    "## ✅ Critérios de Aceite",
    "- [ ] Solução passa em todos os casos de teste",
    "- [ ] Código legível e comentado",
    "- [ ] Complexidade de tempo adequada ao nível",
    "",
    "> 💬 Quando terminar, compartilhe seu código para revisão!",
  ].join("\n");
}

// ── Servidor MCP ─────────────────────────────────────────────────────────────

const server = new McpServer({
  name: "dio-explorer-mcp",
  version: "1.0.0",
});

// ────────────────────────────────────────────────────────────────────────────
// TOOL: buscar_trilha
// ────────────────────────────────────────────────────────────────────────────
server.registerTool(
  "buscar_trilha",
  {
    description:
      "Busca uma trilha de formação DIO por tecnologia e retorna o plano de estudos completo em Markdown (badges, promoção, lives ao vivo).",
    inputSchema: z.object({
      tecnologia: z
        .string()
        .describe('Nome da tecnologia (ex: "Java", "Python", "React", "AWS")'),
    }),
  },
  async ({ tecnologia }) => {
    const trilha = buscarTrilha(tecnologia);
    if (!trilha) {
      const disponiveis = getTrilhasData()
        .trilhas.map((t) => `• ${t.tecnologia}`)
        .join("\n");
      return {
        content: [
          {
            type: "text",
            text: `❌ Nenhuma trilha encontrada para "${tecnologia}".\n\n**Trilhas disponíveis:**\n${disponiveis}`,
          },
        ],
        isError: true,
      };
    }
    return {
      content: [{ type: "text", text: formatarTrilha(trilha) }],
    };
  }
);

// ────────────────────────────────────────────────────────────────────────────
// TOOL: listar_trilhas
// ────────────────────────────────────────────────────────────────────────────
server.registerTool(
  "listar_trilhas",
  {
    description:
      "Lista todas as formações disponíveis no catálogo DIO. Aceita filtro opcional por nível (Básico, Intermediário, Avançado).",
    inputSchema: z.object({
      nivel: z
        .string()
        .optional()
        .describe('Filtrar por nível: "Básico", "Intermediário" ou "Avançado"'),
    }),
  },
  async ({ nivel }) => {
    const trilhas = listarTrilhas(nivel);
    if (trilhas.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `Nenhuma trilha encontrada para o nível "${nivel}".`,
          },
        ],
        isError: true,
      };
    }

    const lista = trilhas
      .map(
        (t) =>
          `| ${t.id} | **${t.nome}** | ${t.tecnologia} | ${t.nivel} | ${t.modulos} módulos | ${t.xp_total} XP | ${t.vitalicio ? "Sim" : "Não"} |`
      )
      .join("\n");

    const texto = [
      `# 📚 Catálogo de Formações DIO${nivel ? ` — ${nivel}` : ""}`,
      "",
      `> ${trilhas.length} formação(ões) encontrada(s).`,
      "",
      "| # | Nome | Tecnologia | Nível | Duração | XP | Vitalício |",
      "|---|------|-----------|-------|---------|-----|-----------|",
      lista,
    ].join("\n");

    return { content: [{ type: "text", text: texto }] };
  }
);

// ────────────────────────────────────────────────────────────────────────────
// TOOL: listar_promocoes
// ────────────────────────────────────────────────────────────────────────────
server.registerTool(
  "listar_promocoes",
  {
    description:
      "Retorna todas as formações DIO que possuem promoção ativa no momento, com desconto e validade.",
    inputSchema: z.object({}),
  },
  async () => {
    const promos = listarProducoes();
    if (promos.length === 0) {
      return {
        content: [{ type: "text", text: "Nenhuma promoção ativa no momento." }],
      };
    }

    const lista = promos
      .map(
        (t) =>
          `| **${t.nome}** | ${t.tecnologia} | 🔥 ${t.promocao.desconto_percentual}% OFF | Até ${t.promocao.validade} |`
      )
      .join("\n");

    return {
      content: [
        {
          type: "text",
          text: [
            "# 🔥 Promoções Ativas DIO",
            "",
            `> ${promos.length} formação(ões) com desconto!`,
            "",
            "| Formação | Tecnologia | Desconto | Válido até |",
            "|---------|-----------|---------|-----------|",
            lista,
          ].join("\n"),
        },
      ],
    };
  }
);

// ────────────────────────────────────────────────────────────────────────────
// TOOL: gerar_desafio
// ────────────────────────────────────────────────────────────────────────────
server.registerTool(
  "gerar_desafio",
  {
    description:
      "Gera um desafio de código aleatório para uma tecnologia e nível escolhidos, com descrição, dicas e critérios de aceite.",
    inputSchema: z.object({
      tecnologia: z
        .string()
        .describe('Tecnologia alvo (ex: "Java", "Python", "TypeScript")'),
      nivel: z
        .string()
        .describe('Nível de dificuldade: "Básico", "Intermediário" ou "Avançado"'),
    }),
  },
  async ({ tecnologia, nivel }) => {
    const texto = sortearDesafio(nivel, tecnologia);
    const isError = texto.startsWith("❌");
    return {
      content: [{ type: "text", text: texto }],
      ...(isError && { isError: true }),
    };
  }
);

// ────────────────────────────────────────────────────────────────────────────
// TOOL: gerar_certificado
// ────────────────────────────────────────────────────────────────────────────
server.registerTool(
  "gerar_certificado",
  {
    description:
      "Gera um certificado de conclusão de formação DIO em Markdown, com nome do aluno, dados da trilha, XP, badge e ID único.",
    inputSchema: z.object({
      nome_aluno: z.string().describe("Nome completo do aluno"),
      tecnologia: z
        .string()
        .describe('Tecnologia/trilha concluída (ex: "Java", "Python")'),
    }),
  },
  async ({ nome_aluno, tecnologia }) => {
    const certificado = gerarCertificado(nome_aluno, tecnologia);
    return {
      content: [{ type: "text", text: certificado }],
    };
  }
);

// ────────────────────────────────────────────────────────────────────────────
// PROMPT: trilha_prompt
// ────────────────────────────────────────────────────────────────────────────
server.registerPrompt(
  "trilha_prompt",
  {
    description: "Template de prompt para explorar o plano de estudos de uma trilha DIO",
    argsSchema: z.object({
      tecnologia: z.string().describe("Tecnologia da trilha"),
    }),
  },
  async ({ tecnologia }) => ({
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text: `Quero explorar a trilha de ${tecnologia} da DIO. Use a ferramenta buscar_trilha para obter o plano de estudos completo e me explique como me organizar para completar a formação em 3 meses.`,
        },
      },
    ],
  })
);

// ────────────────────────────────────────────────────────────────────────────
// PROMPT: desafio_prompt
// ────────────────────────────────────────────────────────────────────────────
server.registerPrompt(
  "desafio_prompt",
  {
    description: "Template de prompt para receber um desafio de código DIO",
    argsSchema: z.object({
      tecnologia: z.string().describe("Tecnologia do desafio"),
      nivel: z.string().describe("Nível do desafio"),
    }),
  },
  async ({ tecnologia, nivel }) => ({
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text: `Gere um desafio de ${nivel} em ${tecnologia} usando a ferramenta gerar_desafio. Depois me mostre a solução passo a passo.`,
        },
      },
    ],
  })
);

// ── Main ─────────────────────────────────────────────────────────────────────

async function main(): Promise<void> {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("✅ DIO Explorer MCP Server rodando via stdio.");
}

main().catch((err) => {
  console.error("❌ Erro fatal:", err);
  process.exit(1);
});
