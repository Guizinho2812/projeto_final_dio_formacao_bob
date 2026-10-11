"""
slash_commands_logic.py
-----------------------
Lógica central dos slash commands /trilha, /desafio e /certificado.
Este módulo é testável de forma isolada — sem dependência do Bob/LLM.
"""

import json
import os
import random
import re
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------- #
# Caminhos base
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent
TRILHAS_DIO_PATH = BASE_DIR / "projeto_final_dio_formacao_bob" / "dio_explorer" / "data" / "trilhas_dio.json"
TRILHAS_PLAYGROUND_PATH = BASE_DIR / "data" / "trilhas.json"
CERTS_OUTPUT_DIR = BASE_DIR / "projeto_final_dio_formacao_bob" / "dio_explorer" / "docs" / "certificados-emitidos"


# --------------------------------------------------------------------------- #
# Utilitários
# --------------------------------------------------------------------------- #

def _load_json(path: Path) -> dict:
    """Carrega e retorna um arquivo JSON. Lança FileNotFoundError se não existir."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _slugify(text: str) -> str:
    """Converte texto para slug (lowercase, hífens)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text


# --------------------------------------------------------------------------- #
# /trilha — busca e formata plano de estudos
# --------------------------------------------------------------------------- #

def buscar_trilha(tecnologia: str, source: str = "dio") -> dict | None:
    """
    Busca a trilha pela tecnologia informada.

    Args:
        tecnologia: nome da tecnologia (case-insensitive, parcial).
        source: 'dio' usa trilhas_dio.json; 'playground' usa data/trilhas.json.

    Returns:
        dict com dados da trilha ou None se não encontrada.
    """
    path = TRILHAS_DIO_PATH if source == "dio" else TRILHAS_PLAYGROUND_PATH
    data = _load_json(path)
    termo = tecnologia.lower().strip()

    if not termo:
        return None

    for trilha in data["trilhas"]:
        # trilhas_dio.json usa campo 'tecnologia' e 'nome'
        campos = [
            trilha.get("tecnologia", "").lower(),
            trilha.get("nome", "").lower(),
        ]
        # trilhas.json também tem 'aliases'
        for alias in trilha.get("aliases", []):
            campos.append(alias.lower())

        if any(termo in campo for campo in campos):
            return trilha

    return None


def listar_tecnologias_disponiveis(source: str = "dio") -> list[str]:
    """Retorna lista com nomes de todas as tecnologias no arquivo."""
    path = TRILHAS_DIO_PATH if source == "dio" else TRILHAS_PLAYGROUND_PATH
    data = _load_json(path)
    return [t.get("tecnologia", t.get("nome", "")) for t in data["trilhas"]]


def formatar_plano_estudos(trilha: dict) -> str:
    """Formata os dados de uma trilha em Markdown."""
    if not trilha:
        return "❌ Trilha não encontrada."

    nome = trilha.get("nome", "—")
    tecnologia = trilha.get("tecnologia", "—")
    nivel = trilha.get("nivel", "—")
    modulos = trilha.get("modulos", 0)
    xp = trilha.get("xp_total", 0)
    vitalicio = "Sim" if trilha.get("vitalicio") else "Não"
    badges = trilha.get("badges", [])
    promocao = trilha.get("promocao", {})
    lives = trilha.get("lives_ao_vivo", [])

    linhas = [
        f"# 🎓 Formação DIO — {nome}",
        "",
        f"**🛠 Tecnologia:** {tecnologia}",
        f"**📊 Nível:** {nivel}",
        f"**📦 Módulos:** {modulos}",
        f"**⭐ XP Total:** {xp} XP",
        f"**♾️ Acesso Vitalício:** {vitalicio}",
        "",
        "---",
        "",
        "## 🏅 Badges Disponíveis",
    ]
    for badge in badges:
        linhas.append(f"🏅 {badge}")

    linhas += ["", "---", "", "## 🎁 Promoção"]
    if promocao.get("ativa"):
        linhas.append(f"🔥 **{promocao['desconto_percentual']}% OFF** — Válido até {promocao['validade']}")
    else:
        linhas.append("Sem promoção ativa no momento.")

    linhas += ["", "---", "", "## 📡 Lives ao Vivo"]
    for live in lives:
        linhas.append(f"🔴 **{live['titulo']}** — {live['data']} · {live['duracao_min']} min")

    return "\n".join(linhas)


# --------------------------------------------------------------------------- #
# /desafio — gerador de desafio de código
# --------------------------------------------------------------------------- #

DESAFIOS = {
    "Básico": [
        ("Algoritmo FizzBuzz", "Imprima números de 1 a N. Múltiplos de 3 → 'Fizz', de 5 → 'Buzz', de ambos → 'FizzBuzz'."),
        ("Palíndromo", "Verifique se uma string é um palíndromo (lê igual de frente para trás)."),
        ("Fatorial Recursivo", "Calcule o fatorial de N usando recursão."),
    ],
    "Intermediário": [
        ("Pilha com Mínimo", "Implemente uma pilha que suporte push, pop e getMin em O(1)."),
        ("Ordenação por Contagem", "Implemente Counting Sort para ordenar um array de inteiros não negativos."),
        ("Consumo de API REST", "Consuma a API pública JSONPlaceholder e exiba os títulos dos 5 primeiros posts."),
    ],
    "Avançado": [
        ("Padrão Observer", "Implemente o padrão Observer com suporte a múltiplos eventos e desinscrição."),
        ("Cache LRU", "Implemente um cache LRU (Least Recently Used) com capacidade configurável em O(1)."),
        ("Pool de Threads", "Crie um pool de threads com fila de tarefas, limite de workers e cancelamento."),
    ],
}

XP_POR_NIVEL = {"Básico": 500, "Intermediário": 1200, "Avançado": 2500}
TEMPO_POR_NIVEL = {"Básico": "30 min", "Intermediário": "1h", "Avançado": "2h"}


def gerar_desafio(tecnologia: str, nivel: str, seed: int | None = None) -> str:
    """
    Gera um desafio de código formatado em Markdown.

    Args:
        tecnologia: linguagem/tecnologia alvo.
        nivel: 'Básico', 'Intermediário' ou 'Avançado'.
        seed: seed para o random (permite testes determinísticos).

    Returns:
        String Markdown com o desafio.
    """
    nivel_norm = nivel.strip().capitalize()
    # normaliza acentuação simples
    nivel_map = {"Basico": "Básico", "Intermediario": "Intermediário", "Avancado": "Avançado"}
    nivel_norm = nivel_map.get(nivel_norm, nivel_norm)

    opcoes = DESAFIOS.get(nivel_norm)
    if not opcoes:
        return f"❌ Nível '{nivel}' inválido. Escolha: Básico, Intermediário ou Avançado."

    rng = random.Random(seed)
    titulo, descricao = rng.choice(opcoes)

    xp = XP_POR_NIVEL.get(nivel_norm, 500)
    tempo = TEMPO_POR_NIVEL.get(nivel_norm, "—")

    return "\n".join([
        f"# ⚔️ Desafio DIO — {tecnologia} · {nivel_norm}",
        "",
        f"**🎯 Tipo:** {titulo}",
        f"**⏱ Tempo estimado:** {tempo}",
        f"**⭐ XP ao concluir:** {xp} XP",
        "",
        "---",
        "",
        "## 📋 Descrição",
        descricao,
        "",
        "## 💡 Dica",
        "Pesquise sobre a estrutura de dados ou padrão mais adequado antes de codificar.",
        "",
        "## ✅ Critérios de Aceite",
        "- [ ] Solução passa em todos os casos de teste",
        "- [ ] Código legível e comentado",
        "- [ ] Complexidade de tempo adequada ao nível",
    ])


# --------------------------------------------------------------------------- #
# /certificado — gerador de certificado
# --------------------------------------------------------------------------- #

def gerar_certificado(nome_usuario: str, tecnologia: str) -> tuple[str, str]:
    """
    Gera certificado em Markdown.

    Args:
        nome_usuario: nome completo do aluno.
        tecnologia: tecnologia/trilha concluída.

    Returns:
        Tupla (conteudo_markdown, nome_arquivo_sugerido).
    """
    trilha = buscar_trilha(tecnologia)

    if trilha:
        nome_formacao = trilha.get("nome", f"Formação {tecnologia}")
        nivel = trilha.get("nivel", "—")
        modulos = trilha.get("modulos", "—")
        xp = trilha.get("xp_total", "—")
        badge = trilha.get("badges", ["—"])[-1]
        sigla = tecnologia[:3].upper()
    else:
        nome_formacao = f"Formação {tecnologia}"
        nivel = "—"
        modulos = "—"
        xp = "—"
        badge = "—"
        sigla = tecnologia[:3].upper()

    hoje = datetime.now()
    data_str = hoje.strftime("%d/%m/%Y")
    cert_id = f"DIO-{hoje.year}{random.randint(1000, 9999)}-{sigla}"

    conteudo = "\n".join([
        "---",
        "",
        "<div align=\"center\">",
        "",
        "# 🎓 CERTIFICADO DE CONCLUSÃO",
        "",
        "### Digital Innovation One — DIO",
        "",
        "---",
        "",
        "## ✨ Certificamos que",
        "",
        f"# {nome_usuario.upper()}",
        "",
        "concluiu com êxito a formação",
        "",
        f"## 🏆 {nome_formacao}",
        "",
        "---",
        "",
        f"**🛠 Tecnologia:** {tecnologia}",
        f"**📊 Nível:** {nivel}",
        f"**📦 Módulos Concluídos:** {modulos}",
        f"**⭐ XP Conquistado:** {xp} XP",
        f"**🏅 Badge de Conclusão:** {badge}",
        "",
        "---",
        "",
        f"**📅 Data de Emissão:** {data_str}",
        f"**🔑 ID do Certificado:** {cert_id}",
        "",
        "---",
        "",
        "> *\"A jornada de mil milhas começa com um único passo.\"*",
        "",
        "---",
        "",
        "🌐 [dio.me](https://www.dio.me) · Plataforma de Educação em Tecnologia",
        "",
        "</div>",
        "",
        "---",
    ])

    nome_arquivo = f"certificado-{_slugify(nome_usuario)}-{_slugify(tecnologia)}.md"
    return conteudo, nome_arquivo


def salvar_certificado(conteudo: str, nome_arquivo: str) -> Path:
    """Persiste o certificado em disco e retorna o caminho final."""
    CERTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    destino = CERTS_OUTPUT_DIR / nome_arquivo
    destino.write_text(conteudo, encoding="utf-8")
    return destino
