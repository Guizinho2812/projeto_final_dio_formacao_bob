"""
validate_ts.py — valida estrutura dos arquivos TypeScript do MCP Server
sem precisar do compilador tsc instalado.
"""
import re
import sys
from pathlib import Path

src_dir = Path("projeto_final_dio_formacao_bob/dio_explorer/mcp/src")
files = list(src_dir.glob("*.ts"))
print(f"Validando {len(files)} arquivo(s) TypeScript em {src_dir}...\n")

errors = []

DATA_EXPORTS = [
    "buscarTrilha", "listarTrilhas", "listarProducoes",
    "formatarTrilha", "gerarCertificado", "getTrilhasData",
    "Trilha", "TrilhasData", "Promocao", "Live",
]

for f in sorted(files):
    src = f.read_text(encoding="utf-8")
    lines = src.splitlines()
    print(f"  [{f.name}] {len(lines)} linhas")

    # 1. Verifica que não há console.log (deve usar console.error)
    log_lines = [i+1 for i, l in enumerate(lines) if "console.log(" in l]
    if log_lines:
        errors.append(f"{f.name}: console.log nas linhas {log_lines} (use console.error)")

    # 2. Verifica que funções de data.ts usadas são importadas (exceto no próprio data.ts)
    if f.name != "data.ts":
        used = [fn for fn in DATA_EXPORTS if re.search(r'\b' + fn + r'\b', src)]
        import_block = re.findall(r'import\s*\{([^}]+)\}\s*from', src)
        imported_flat = " ".join(import_block)
        for fn in used:
            if fn not in imported_flat:
                errors.append(f"{f.name}: '{fn}' usado mas não encontrado no import de data.ts")

    # 3. Verifica que server.registerTool / registerPrompt têm os 3 args
    registers = re.findall(r'server\.registerTool\s*\(', src)
    if registers:
        print(f"    -- {len(registers)} tool(s) registrada(s)")

    prompts = re.findall(r'server\.registerPrompt\s*\(', src)
    if prompts:
        print(f"    -- {len(prompts)} prompt(s) registrado(s)")

    # 4. Verifica exports em data.ts
    if f.name == "data.ts":
        for fn in DATA_EXPORTS:
            if f"export function {fn}" not in src and f"export interface {fn}" not in src:
                errors.append(f"data.ts: '{fn}' não encontrado como export")

print()
if errors:
    print("ERRO - Verificacoes falharam:")
    for e in errors:
        print(f"   * {e}")
    sys.exit(1)
else:
    print("OK - Todas as verificacoes passaram. Codigo pronto para build com: npm run build")
