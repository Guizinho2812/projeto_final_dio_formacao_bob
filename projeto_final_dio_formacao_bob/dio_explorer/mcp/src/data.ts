/**
 * data.ts — camada de acesso aos dados de trilhas
 * Lê o arquivo trilhas_dio.json e expõe funções de consulta reutilizáveis
 * tanto pelo servidor MCP (stdio) quanto pelo servidor HTTP.
 */

import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// ── Tipos ────────────────────────────────────────────────────────────────────

export interface Promocao {
  ativa: boolean;
  desconto_percentual: number;
  validade: string | null;
}

export interface Live {
  titulo: string;
  data: string;
  duracao_min: number;
}

export interface Trilha {
  id: number;
  nome: string;
  tecnologia: string;
  nivel: string;
  modulos: number;
  xp_total: number;
  badges: string[];
  promocao: Promocao;
  vitalicio: boolean;
  lives_ao_vivo: Live[];
}

export interface TrilhasData {
  trilhas: Trilha[];
}

// ── Carregamento do JSON ─────────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function loadTrilhas(): TrilhasData {
  const jsonPath = process.env.TRILHAS_JSON_PATH
    ? resolve(process.env.TRILHAS_JSON_PATH)
    : resolve(__dirname, "../../data/trilhas_dio.json");

  const raw = readFileSync(jsonPath, "utf-8");
  return JSON.parse(raw) as TrilhasData;
}

// Cache em memória (recarrega se o módulo for recarregado)
let _cache: TrilhasData | null = null;

export function getTrilhasData(): TrilhasData {
  if (!_cache) _cache = loadTrilhas();
  return _cache;
}

// ── Funções de consulta ──────────────────────────────────────────────────────

/**
 * Busca uma trilha por tecnologia (parcial, case-insensitive).
 */
export function buscarTrilha(tecnologia: string): Trilha | undefined {
  const termo = tecnologia.toLowerCase().trim();
  if (!termo) return undefined;
  const { trilhas } = getTrilhasData();
  return trilhas.find(
    (t) =>
      t.tecnologia.toLowerCase().includes(termo) ||
      t.nome.toLowerCase().includes(termo)
  );
}

/**
 * Retorna todas as trilhas, com filtro opcional por nível.
 */
export function listarTrilhas(nivel?: string): Trilha[] {
  const { trilhas } = getTrilhasData();
  if (!nivel) return trilhas;
  const n = nivel.toLowerCase();
  return trilhas.filter((t) => t.nivel.toLowerCase().includes(n));
}

/**
 * Retorna trilhas com promoção ativa.
 */
export function listarProducoes(): Trilha[] {
  const { trilhas } = getTrilhasData();
  return trilhas.filter((t) => t.promocao.ativa);
}

/**
 * Formata os dados de uma trilha em Markdown legível.
 */
export function formatarTrilha(t: Trilha): string {
  const vitalicio = t.vitalicio ? "Sim ♾️" : "Não";
  const promocao = t.promocao.ativa
    ? `🔥 **${t.promocao.desconto_percentual}% OFF** — Válido até ${t.promocao.validade}`
    : "Sem promoção ativa no momento.";

  const badgesList = t.badges.map((b) => `🏅 ${b}`).join("\n");
  const livesList = t.lives_ao_vivo
    .map((l) => `🔴 **${l.titulo}** — ${l.data} · ${l.duracao_min} min`)
    .join("\n");

  return [
    `# 🎓 Formação DIO — ${t.nome}`,
    "",
    `**🛠 Tecnologia:** ${t.tecnologia}`,
    `**📊 Nível:** ${t.nivel}`,
    `**📦 Módulos:** ${t.modulos}`,
    `**⭐ XP Total:** ${t.xp_total} XP`,
    `**♾️ Acesso Vitalício:** ${vitalicio}`,
    "",
    "---",
    "",
    "## 🏅 Badges Disponíveis",
    badgesList,
    "",
    "---",
    "",
    "## 🎁 Promoção",
    promocao,
    "",
    "---",
    "",
    "## 📡 Lives ao Vivo",
    livesList || "_Nenhuma live agendada._",
  ].join("\n");
}

/**
 * Gera um certificado em Markdown para um aluno.
 */
export function gerarCertificado(nomeAluno: string, tecnologia: string): string {
  const trilha = buscarTrilha(tecnologia);
  const hoje = new Date();
  const data = hoje.toLocaleDateString("pt-BR");
  const ano = hoje.getFullYear();
  const rand = Math.floor(1000 + Math.random() * 9000);

  const nomeFormacao = trilha?.nome ?? `Formação ${tecnologia}`;
  const nivel = trilha?.nivel ?? "—";
  const modulos = trilha?.modulos ?? "—";
  const xp = trilha?.xp_total ?? "—";
  const badge = trilha?.badges?.at(-1) ?? "—";
  const sigla = tecnologia.slice(0, 3).toUpperCase().replace(/[^A-Z]/g, "X");
  const certId = `DIO-${ano}${rand}-${sigla}`;

  return [
    "---",
    "",
    '<div align="center">',
    "",
    "# 🎓 CERTIFICADO DE CONCLUSÃO",
    "",
    "### Digital Innovation One — DIO",
    "",
    "---",
    "",
    "## ✨ Certificamos que",
    "",
    `# ${nomeAluno.toUpperCase()}`,
    "",
    "concluiu com êxito a formação",
    "",
    `## 🏆 ${nomeFormacao}`,
    "",
    "---",
    "",
    `**🛠 Tecnologia:** ${tecnologia}`,
    `**📊 Nível:** ${nivel}`,
    `**📦 Módulos Concluídos:** ${modulos}`,
    `**⭐ XP Conquistado:** ${xp} XP`,
    `**🏅 Badge de Conclusão:** ${badge}`,
    "",
    "---",
    "",
    `**📅 Data de Emissão:** ${data}`,
    `**🔑 ID do Certificado:** ${certId}`,
    "",
    "---",
    "",
    '> *"A jornada de mil milhas começa com um único passo."*',
    "",
    "---",
    "",
    "🌐 [dio.me](https://www.dio.me) · Plataforma de Educação em Tecnologia",
    "",
    "</div>",
    "",
    "---",
  ].join("\n");
}
