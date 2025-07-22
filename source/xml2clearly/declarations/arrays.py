from source.xml2clearly.xml_manager import Tag


def parse_array_dimensions(name_tag: Tag):
    """
    Extrai os tamanhos das dimensões de um nome de array a partir das tags <index>.
    Exemplo: arr[5][10] -> [5, 10]
    """
    dims = []
    for child in name_tag.children:
        if child.name == "index":
            expr = child.find_children("expr")
            if expr:
                dims.append(expr[0].text)
    return dims


def format_array_type(base_type: str, dimensions: list[str]) -> str:
    """
    Constrói a representação do tipo array com base no tipo base e nas dimensões.
    Exemplo: int + [5, 10] -> array(5, array(10, int))
    """
    for size in reversed(dimensions):
        base_type = f"array({size}, {base_type})"
    return base_type


def translate_array_decl(tag: Tag) -> str:
    type_tag = tag.find_children("type")[0] if tag.find_children("type") else None
    name_tag = tag.find_children("name")[0] if tag.find_children("name") else None
    init_tag = tag.find_children("init")

    if not (type_tag and name_tag):
        return "UNKNOWN_ARRAY_DECL"

    # Tipo base (ignorando indexações)
    base_type_parts = [c.text for c in type_tag.walk() if c.name in {"name", "specifier"}]
    base_type = " ".join(base_type_parts)

    # Nome do array
    array_name = name_tag.text

    # Dimensões
    dimensions = parse_array_dimensions(name_tag)
    full_type = format_array_type(base_type, dimensions)

    result = f"{array_name}: {full_type}"

    # Inicialização, se houver
    if init_tag:
        block = init_tag[0].search("block")
        if block:
            values = extract_initializer_values(block[0])
            result += f" = {values}"

    return result


def extract_initializer_values(block_tag: Tag):
    """
    Extrai os valores de inicialização do bloco em forma de lista ou listas aninhadas.
    """
    values = []
    for child in block_tag.children:
        if child.name == "expr":
            if child.children and child.children[0].name == "block":
                # Caso aninhado
                nested = extract_initializer_values(child.children[0])
                values.append(nested)
            else:
                val = "".join(grand.text for grand in child.children if grand.text)
                values.append(val)
    return str(values).replace("'", "")


def extract_array_declarations(tag: Tag) -> list[str]:
    """
    Extrai e traduz todas as declarações de arrays a partir de um <unit>.
    """
    translated = []
    for decl_stmt in tag.search("decl_stmt"):
        for decl in decl_stmt.find_children("decl"):
            name_children = decl.search("name")
            if any(nc.name == "index" or nc.find_children("index") for nc in name_children):
                translated.append(translate_array_decl(decl))
    return translated
