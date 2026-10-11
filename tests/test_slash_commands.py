"""
test_slash_commands.py
----------------------
Suite de testes unitários para os slash commands /trilha, /desafio e /certificado.
Aluno-alvo dos testes de integração: "Carlos Alves" | Trilha: Java

Execute com:
    python -m pytest tests/test_slash_commands.py -v --tb=short

Para cobertura:
    python -m pytest tests/test_slash_commands.py -v --tb=short \
        --cov=tests.slash_commands_logic --cov-report=term-missing
"""

import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ── garante que o módulo de lógica seja encontrado ──────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
import slash_commands_logic as scl

# ── fixture: aluno dos testes de integração ─────────────────────────────────
ALUNO_NOME = "Carlos Alves"
ALUNO_TECNOLOGIA = "Java"
ALUNO_NIVEL = "Intermediário"


# ===========================================================================
# GRUPO 1 — /trilha
# ===========================================================================

class TestTrilhaBuscaJava:
    """Testes do comando /trilha com tecnologia Java."""

    def test_buscar_trilha_java_exata(self):
        """Busca exata por 'Java' deve retornar a trilha Java Developer."""
        trilha = scl.buscar_trilha("Java")
        assert trilha is not None, "Trilha Java não encontrada no JSON"
        assert trilha["tecnologia"] == "Java"

    def test_buscar_trilha_java_case_insensitive(self):
        """Busca case-insensitive: 'java', 'JAVA', 'JaVa' devem encontrar."""
        for variante in ["java", "JAVA", "JaVa"]:
            trilha = scl.buscar_trilha(variante)
            assert trilha is not None, f"Falhou para variante '{variante}'"
            assert trilha["tecnologia"] == "Java"

    def test_buscar_trilha_java_parcial(self):
        """Busca parcial: 'jav' deve encontrar Java."""
        trilha = scl.buscar_trilha("jav")
        assert trilha is not None
        assert "Java" in trilha["tecnologia"]

    def test_trilha_java_tem_campos_obrigatorios(self):
        """Trilha Java deve conter todos os campos esperados."""
        trilha = scl.buscar_trilha("Java")
        campos = ["id", "nome", "tecnologia", "nivel", "modulos", "xp_total", "badges"]
        for campo in campos:
            assert campo in trilha, f"Campo '{campo}' ausente na trilha Java"

    def test_trilha_java_nivel_intermediario(self):
        """Trilha Java deve ter nível Intermediário conforme o JSON."""
        trilha = scl.buscar_trilha("Java")
        assert trilha["nivel"] == "Intermediário"

    def test_trilha_java_modulos_maior_zero(self):
        """Trilha Java deve ter pelo menos 1 módulo."""
        trilha = scl.buscar_trilha("Java")
        assert trilha["modulos"] > 0

    def test_trilha_java_xp_total_positivo(self):
        """XP total da trilha Java deve ser positivo."""
        trilha = scl.buscar_trilha("Java")
        assert trilha["xp_total"] > 0

    def test_trilha_java_badges_nao_vazios(self):
        """Badges da trilha Java não devem estar vazios."""
        trilha = scl.buscar_trilha("Java")
        assert len(trilha["badges"]) > 0


class TestTrilhaBuscaGeneral:
    """Testes gerais do comando /trilha."""

    def test_tecnologia_inexistente_retorna_none(self):
        """Tecnologia não cadastrada deve retornar None."""
        resultado = scl.buscar_trilha("COBOL")
        assert resultado is None

    def test_tecnologia_vazia_retorna_none(self):
        """String vazia deve retornar None."""
        resultado = scl.buscar_trilha("")
        assert resultado is None

    def test_listar_tecnologias_retorna_lista(self):
        """listar_tecnologias_disponiveis deve retornar lista não vazia."""
        techs = scl.listar_tecnologias_disponiveis()
        assert isinstance(techs, list)
        assert len(techs) > 0

    def test_listar_tecnologias_contem_java(self):
        """Java deve estar na lista de tecnologias disponíveis."""
        techs = scl.listar_tecnologias_disponiveis()
        assert any("Java" in t for t in techs)

    def test_buscar_python(self):
        """Busca por 'Python' deve funcionar."""
        trilha = scl.buscar_trilha("Python")
        assert trilha is not None

    def test_buscar_react(self):
        """Busca por 'React' deve funcionar."""
        trilha = scl.buscar_trilha("React")
        assert trilha is not None

    def test_arquivo_json_existe(self):
        """O arquivo trilhas_dio.json deve existir no caminho configurado."""
        assert scl.TRILHAS_DIO_PATH.exists(), f"Arquivo não encontrado: {scl.TRILHAS_DIO_PATH}"

    def test_arquivo_json_valido(self):
        """O JSON de trilhas deve ser válido e conter chave 'trilhas'."""
        data = scl._load_json(scl.TRILHAS_DIO_PATH)
        assert "trilhas" in data
        assert isinstance(data["trilhas"], list)

    def test_load_json_arquivo_inexistente(self):
        """_load_json deve lançar FileNotFoundError para arquivo inexistente."""
        with pytest.raises(FileNotFoundError):
            scl._load_json(Path("/nao/existe/arquivo.json"))


class TestTrilhaFormatacao:
    """Testes de formatação da saída do /trilha."""

    def test_formatar_plano_retorna_string(self):
        """formatar_plano_estudos deve retornar uma string."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert isinstance(resultado, str)

    def test_formatar_plano_contem_nome(self):
        """Plano formatado deve conter o nome da formação."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert "Java" in resultado

    def test_formatar_plano_contem_nivel(self):
        """Plano formatado deve exibir o nível da trilha."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert "Intermediário" in resultado

    def test_formatar_plano_contem_xp(self):
        """Plano formatado deve exibir o XP total."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert "XP" in resultado

    def test_formatar_plano_contem_badges(self):
        """Plano formatado deve listar os badges."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        for badge in trilha["badges"]:
            assert badge in resultado

    def test_formatar_plano_sem_promocao(self):
        """Trilha sem promoção deve exibir mensagem adequada."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert "Sem promoção ativa" in resultado

    def test_formatar_plano_none_retorna_erro(self):
        """formatar_plano_estudos com None deve retornar mensagem de erro."""
        resultado = scl.formatar_plano_estudos(None)
        assert "❌" in resultado

    def test_formatar_plano_contem_lives(self):
        """Plano formatado deve listar as lives ao vivo."""
        trilha = scl.buscar_trilha("Java")
        resultado = scl.formatar_plano_estudos(trilha)
        assert "Lives ao Vivo" in resultado
        for live in trilha["lives_ao_vivo"]:
            assert live["titulo"] in resultado


# ===========================================================================
# GRUPO 2 — /desafio
# ===========================================================================

class TestDesafioJava:
    """Testes do comando /desafio para o aluno Carlos Alves — Java Intermediário."""

    def test_gerar_desafio_java_intermediario(self):
        """Deve gerar desafio Java Intermediário sem erros."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_desafio_contem_tecnologia(self):
        """Desafio deve mencionar a tecnologia Java."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert "Java" in resultado

    def test_desafio_contem_nivel(self):
        """Desafio deve mencionar o nível Intermediário."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert "Intermediário" in resultado

    def test_desafio_contem_xp(self):
        """Desafio Intermediário deve exibir 1200 XP."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert "1200" in resultado

    def test_desafio_contem_tempo(self):
        """Desafio Intermediário deve exibir tempo de 1h."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert "1h" in resultado

    def test_desafio_contem_criterios_aceite(self):
        """Desafio deve conter seção de critérios de aceite."""
        resultado = scl.gerar_desafio(ALUNO_TECNOLOGIA, ALUNO_NIVEL, seed=42)
        assert "Critérios de Aceite" in resultado

    def test_desafio_seed_determinisico(self):
        """Mesma seed deve gerar exatamente o mesmo desafio."""
        r1 = scl.gerar_desafio("Java", "Intermediário", seed=99)
        r2 = scl.gerar_desafio("Java", "Intermediário", seed=99)
        assert r1 == r2

    def test_desafio_seeds_diferentes_podem_divergir(self):
        """Seeds diferentes PODEM gerar desafios distintos."""
        r1 = scl.gerar_desafio("Java", "Intermediário", seed=1)
        r2 = scl.gerar_desafio("Java", "Intermediário", seed=999)
        # não é garantido (pequeno pool), mas é o comportamento esperado
        # apenas verifica que ambos são strings válidas
        assert isinstance(r1, str) and isinstance(r2, str)


class TestDesafioNiveis:
    """Testes dos diferentes níveis do /desafio."""

    def test_nivel_basico_xp_500(self):
        """Desafio Básico deve ter 500 XP."""
        resultado = scl.gerar_desafio("Python", "Básico", seed=1)
        assert "500" in resultado

    def test_nivel_avancado_xp_2500(self):
        """Desafio Avançado deve ter 2500 XP."""
        resultado = scl.gerar_desafio("Python", "Avançado", seed=1)
        assert "2500" in resultado

    def test_nivel_avancado_tempo_2h(self):
        """Desafio Avançado deve ter tempo de 2h."""
        resultado = scl.gerar_desafio("Python", "Avançado", seed=1)
        assert "2h" in resultado

    def test_nivel_invalido_retorna_erro(self):
        """Nível inválido deve retornar mensagem de erro com ❌."""
        resultado = scl.gerar_desafio("Java", "Gigante", seed=1)
        assert "❌" in resultado

    def test_nivel_normalizado_sem_acento(self):
        """'Basico' sem acento deve ser normalizado para 'Básico'."""
        resultado = scl.gerar_desafio("Java", "Basico", seed=1)
        assert "❌" not in resultado

    def test_nivel_normalizado_intermediario_sem_acento(self):
        """'Intermediario' sem acento deve ser normalizado."""
        resultado = scl.gerar_desafio("Java", "Intermediario", seed=1)
        assert "❌" not in resultado


# ===========================================================================
# GRUPO 3 — /certificado
# ===========================================================================

class TestCertificadoJava:
    """Testes do /certificado para Carlos Alves — Trilha Java."""

    def test_gerar_certificado_retorna_tupla(self):
        """gerar_certificado deve retornar uma tupla (conteudo, nome_arquivo)."""
        resultado = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2

    def test_certificado_contem_nome_usuario(self):
        """Certificado deve conter o nome do aluno em maiúsculas."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert ALUNO_NOME.upper() in conteudo

    def test_certificado_contem_tecnologia(self):
        """Certificado deve mencionar a tecnologia Java."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "Java" in conteudo

    def test_certificado_contem_nome_formacao(self):
        """Certificado deve conter o nome oficial da formação."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "Formação Java Developer" in conteudo

    def test_certificado_contem_nivel(self):
        """Certificado deve exibir o nível da trilha."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "Intermediário" in conteudo

    def test_certificado_contem_xp(self):
        """Certificado deve exibir o XP total conquistado."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "18000" in conteudo

    def test_certificado_contem_badge_conclusao(self):
        """Certificado deve exibir o último badge da trilha Java."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "JPA Warrior" in conteudo  # último badge da trilha Java

    def test_certificado_contem_id(self):
        """Certificado deve ter um ID no formato DIO-AAAA????-JAV."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert re.search(r"DIO-\d{8}-JAV", conteudo)

    def test_certificado_contem_data_atual(self):
        """Certificado deve conter o ano atual na data de emissão."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert str(datetime.now().year) in conteudo

    def test_nome_arquivo_slug(self):
        """Nome do arquivo deve ser slugificado corretamente."""
        _, nome_arquivo = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert nome_arquivo == "certificado-carlos-alves-java.md"

    def test_certificado_contem_dio_link(self):
        """Certificado deve conter referência ao dio.me."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "dio.me" in conteudo

    def test_certificado_contem_markdown_div(self):
        """Certificado deve ter a div de alinhamento central."""
        conteudo, _ = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        assert "<div align=\"center\">" in conteudo

    def test_certificado_tecnologia_inexistente(self):
        """Certificado para tecnologia inexistente deve ser gerado com fallback."""
        conteudo, nome_arquivo = scl.gerar_certificado("Maria Silva", "COBOL")
        assert "MARIA SILVA" in conteudo
        assert "COBOL" in conteudo
        assert "certificado-maria-silva-cobol.md" == nome_arquivo


class TestCertificadoSalvar:
    """Testes de persistência do /certificado."""

    def test_salvar_certificado_cria_arquivo(self, tmp_path, monkeypatch):
        """salvar_certificado deve criar o arquivo no diretório correto."""
        monkeypatch.setattr(scl, "CERTS_OUTPUT_DIR", tmp_path)
        conteudo, nome = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        caminho = scl.salvar_certificado(conteudo, nome)
        assert caminho.exists()
        assert caminho.read_text(encoding="utf-8") == conteudo

    def test_salvar_certificado_retorna_path(self, tmp_path, monkeypatch):
        """salvar_certificado deve retornar um objeto Path."""
        monkeypatch.setattr(scl, "CERTS_OUTPUT_DIR", tmp_path)
        conteudo, nome = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        resultado = scl.salvar_certificado(conteudo, nome)
        assert isinstance(resultado, Path)

    def test_salvar_cria_diretorio_se_inexistente(self, tmp_path, monkeypatch):
        """Deve criar o diretório de destino se não existir."""
        novo_dir = tmp_path / "subdir" / "certs"
        monkeypatch.setattr(scl, "CERTS_OUTPUT_DIR", novo_dir)
        conteudo, nome = scl.gerar_certificado(ALUNO_NOME, ALUNO_TECNOLOGIA)
        scl.salvar_certificado(conteudo, nome)
        assert novo_dir.exists()


# ===========================================================================
# GRUPO 4 — Utilitários
# ===========================================================================

class TestUtilitarios:
    """Testes das funções utilitárias internas."""

    def test_slugify_simples(self):
        assert scl._slugify("Carlos Alves") == "carlos-alves"

    def test_slugify_maiusculas(self):
        assert scl._slugify("JAVA DEVELOPER") == "java-developer"

    def test_slugify_espacos_multiplos(self):
        assert scl._slugify("  Python   Developer  ") == "python-developer"

    def test_slugify_caracteres_especiais(self):
        resultado = scl._slugify("React.js & TypeScript!")
        assert " " not in resultado
        assert resultado == resultado.lower()

    def test_slugify_string_vazia(self):
        assert scl._slugify("") == ""


# ===========================================================================
# GRUPO 5 — Fluxo de integração completo (Carlos Alves / Java)
# ===========================================================================

class TestFluxoIntegracaoCarlosJava:
    """
    Teste end-to-end simulando o fluxo completo do aluno Carlos Alves
    na Trilha Java: /trilha → /desafio → /certificado.
    """

    def test_fluxo_completo(self, tmp_path, monkeypatch):
        """
        Executa o fluxo completo:
          1. /trilha Java   → localiza e formata o plano de estudos
          2. /desafio Java Intermediário → gera desafio para o aluno
          3. /certificado Carlos Alves Java → gera e salva o certificado
        """
        monkeypatch.setattr(scl, "CERTS_OUTPUT_DIR", tmp_path)

        # ── 1. /trilha ───────────────────────────────────────────────────────
        trilha = scl.buscar_trilha("Java")
        assert trilha is not None, "FALHA /trilha: Java não encontrada"

        plano = scl.formatar_plano_estudos(trilha)
        assert "Java" in plano, "FALHA /trilha: nome da tecnologia ausente no plano"
        assert "Intermediário" in plano, "FALHA /trilha: nível ausente no plano"

        # ── 2. /desafio ──────────────────────────────────────────────────────
        desafio = scl.gerar_desafio("Java", "Intermediário", seed=7)
        assert "Java" in desafio, "FALHA /desafio: tecnologia ausente"
        assert "1200" in desafio, "FALHA /desafio: XP Intermediário incorreto"
        assert "Critérios de Aceite" in desafio, "FALHA /desafio: critérios ausentes"

        # ── 3. /certificado ──────────────────────────────────────────────────
        conteudo, nome_arquivo = scl.gerar_certificado("Carlos Alves", "Java")
        assert "CARLOS ALVES" in conteudo, "FALHA /certificado: nome do aluno ausente"
        assert "JPA Warrior" in conteudo, "FALHA /certificado: badge de conclusão ausente"

        caminho = scl.salvar_certificado(conteudo, nome_arquivo)
        assert caminho.exists(), "FALHA /certificado: arquivo não foi salvo"
        assert caminho.name == "certificado-carlos-alves-java.md"
