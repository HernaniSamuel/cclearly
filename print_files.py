#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def should_ignore(path_str):
    """Verifica se um caminho deve ser ignorado"""
    ignore_dirs = {
        '.venv', '.idea', '.git', '__pycache__', '.pytest_cache',
        'node_modules', '.mypy_cache', 'dist', 'build', '.tox',
        'venv', 'env', '.env', 'htmlcov', '.coverage', '.vscode',
        'target', 'out', 'bin', 'obj'
    }

    ignore_files = {
        '.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep',
        'poetry.lock', 'package-lock.json', 'yarn.lock'
    }

    ignore_extensions = {
        '.pyc', '.pyo', '.pyd', '.log', '.tmp', '.temp',
        '.cache', '.sqlite', '.db', '.exe', '.dll', '.so',
        '.o', '.class', '.jar'
    }

    path = Path(path_str)

    # Verifica se alguma parte do caminho está nos diretórios ignorados
    for part in path.parts:
        if part in ignore_dirs:
            return True
        # Ignora arquivos/pastas ocultos (começam com .)
        if part.startswith('.') and part not in {'.', '..'}:
            return True

    # Verifica nome do arquivo
    if path.name in ignore_files:
        return True

    # Verifica extensão
    if path.suffix in ignore_extensions:
        return True

    return False


def list_files(base_dir=".", extensions=None, filters=None):
    """Lista arquivos com extensões específicas"""
    if extensions is None:
        extensions = set()  # Todos os arquivos se não especificado

    if filters is None:
        filters = []

    files = []
    base_path = Path(base_dir).resolve()

    for root, dirs, filenames in os.walk(base_path):
        # Remove diretórios ignorados
        dirs[:] = [d for d in dirs if not should_ignore(d)]

        for filename in filenames:
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(base_path)

            # Verifica se deve ignorar
            if should_ignore(str(rel_path)):
                continue

            # Verifica extensão (se especificada)
            if extensions and file_path.suffix.lower() not in extensions:
                continue

            # Verifica filtros (se especificados)
            if filters:
                file_name = file_path.name.lower()
                if not any(filt.lower() in file_name for filt in filters):
                    continue

            files.append(rel_path)

    return sorted(files)


def show_usage():
    """Mostra como usar o script"""
    print("""
📁 Uso: python list_files.py [opções] [filtros...]

📋 Opções:
  --ext .py,.js,.c     Extensões de arquivo (padrão: todos)
  --dir caminho        Diretório base (padrão: .)
  --tree              Mostra em formato árvore
  --help              Mostra esta ajuda

🔍 Filtros (nome do arquivo deve conter):
  python list_files.py main test     # Arquivos com 'main' ou 'test' no nome

📁 Exemplos:
  python list_files.py                    # Todos os arquivos
  python list_files.py --ext .py          # Apenas .py
  python list_files.py --ext .js,.css     # JS e CSS
  python list_files.py --tree             # Formato árvore
  python list_files.py main config        # Com 'main' ou 'config'
""")


def print_tree(files):
    """Imprime arquivos em formato árvore"""
    if not files:
        return

    # Agrupa por diretório
    dirs = {}
    for file_path in files:
        parts = file_path.parts
        if len(parts) == 1:
            # Arquivo na raiz
            dirs.setdefault(".", []).append(parts[0])
        else:
            # Arquivo em subdiretório
            dir_path = str(Path(*parts[:-1]))
            dirs.setdefault(dir_path, []).append(parts[-1])

    # Imprime estrutura
    root_files = dirs.get(".", [])
    if root_files:
        for f in sorted(root_files):
            print(f"📄 {f}")

    # Imprime diretórios
    for dir_path in sorted(d for d in dirs.keys() if d != "."):
        print(f"\n📁 {dir_path}/")
        for f in sorted(dirs[dir_path]):
            print(f"  📄 {f}")


def main():
    if '--help' in sys.argv:
        show_usage()
        return

    # Parâmetros padrão
    extensions = set()
    base_dir = "."
    filters = []
    tree_mode = False

    # Parse dos argumentos
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '--ext' and i + 1 < len(sys.argv):
            ext_str = sys.argv[i + 1]
            extensions = {ext.strip() for ext in ext_str.split(',')}
            i += 2
        elif arg == '--dir' and i + 1 < len(sys.argv):
            base_dir = sys.argv[i + 1]
            i += 2
        elif arg == '--tree':
            tree_mode = True
            i += 1
        elif not arg.startswith('--'):
            filters.append(arg)
            i += 1
        else:
            i += 1

    # Lista arquivos
    files = list_files(base_dir, extensions, filters)

    if not files:
        print("❌ Nenhum arquivo encontrado!")
        return

    print(f"📁 Diretório: {Path(base_dir).resolve()}")
    if extensions:
        print(f"📄 Extensões: {', '.join(extensions)}")
    if filters:
        print(f"🔍 Filtros: {', '.join(filters)}")
    print(f"✅ {len(files)} arquivo(s) encontrado(s)")
    print()

    if tree_mode:
        print_tree(files)
    else:
        # Lista simples
        for file_path in files:
            print(file_path)


if __name__ == "__main__":
    main()