import os

def listar_arquivos_py(base_dir):
    arquivos_py = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".py"):
                arquivos_py.append(os.path.join(root, f))
    return arquivos_py

def mostrar_arquivos(arquivos):
    for path in arquivos:
        print(f"\n{'=' * 80}")
        print(f"# Arquivo: {path}")
        print(f"{'=' * 80}")
        with open(path, 'r', encoding='utf-8') as file:
            print(file.read())

if __name__ == "__main__":
    BASE = "source"  # ou "." se quiser pegar tudo
    arquivos = listar_arquivos_py(BASE)

    # Se quiser limitar por nomes, edite aqui:
    filtros = [

        "registry",
        "arrays",
        "base",
        "comments",
        "__init__"
        # adicione o que quiser
    ]

    selecionados = [a for a in arquivos if any(f in a for f in filtros)]

    if not selecionados:
        print("Nenhum arquivo .py encontrado com os filtros fornecidos.")
    else:
        mostrar_arquivos(selecionados)
