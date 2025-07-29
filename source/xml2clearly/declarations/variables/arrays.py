from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.registry import register
from source.xml2clearly.declarations.variables.helpers import translate_type


@register("decl", priority=20)
def translate_decl_array(tag: Tag) -> str:
    """
    Traduz declarações de arrays, incluindo inicializações.

    Exemplos:
    - int a[2] = {1,2} -> a: array(2, int) = [1, 2]
    - int b[3][2] -> b: array(3, array(2, int))
    - int c[], d[10] -> c: array(?, int), d: array(10, int)
    """
    from source.xml2clearly.translate import translate

    if not is_array_tag(tag):
        return translate_base_decl(tag)

    # Extrair informações básicas
    var_name = extract_variable_name(tag)
    base_type = extract_base_type(tag)
    array_type = build_array_type(tag, base_type, translate)

    # Verificar se há inicialização
    init_tag = tag.find_children("init")
    if init_tag:
        init_str = translate_array_init(init_tag[0], translate)
        return f"{var_name}: {array_type} = {init_str}"
    else:
        return f"{var_name}: {array_type}"


@register("block", priority=50)
def translate_array_block(tag: Tag) -> str:
    """
    Traduz blocos de inicialização de arrays aninhados, transformando { ... } em [ ... ] corretamente.

    Exemplo:
    - {1, 2, 3}          -> [1, 2, 3]
    - {{1, 2}, {3, 4}}   -> [[1, 2], [3, 4]]
    """
    from source.xml2clearly.translate import translate

    # Verifica se é um bloco de inicialização de array
    if not is_array_initialization_block(tag):
        return None  # Deixa outros tradutores lidarem

    def translate_block_recursively(block_tag: Tag) -> str:
        elements = []

        for child in block_tag.children:
            if isinstance(child, Tag):
                if child.name == "expr":
                    # Cada expr pode conter blocos ou literais
                    translated = translate_expr_recursively(child)
                    if translated is not None:
                        elements.append(translated)

        return "[" + ", ".join(elements) + "]"

    def translate_expr_recursively(expr_tag: Tag) -> str | None:
        """
        Trata expr que pode conter:
        - literal -> retorna direto
        - block -> processa recursivamente
        """
        for child in expr_tag.children:
            if isinstance(child, Tag):
                if child.name == "block":
                    return translate_block_recursively(child)
                else:
                    return translate(child).strip()
        return None

    return translate_block_recursively(tag)

def is_array_tag(tag: Tag) -> bool:
    """Verifica se a tag representa uma declaração de array."""
    for name_tag in tag.find_children("name"):
        if has_index_children(name_tag):
            return True
    return False


def has_index_children(tag: Tag) -> bool:
    """Verifica se a tag tem filhos do tipo 'index'."""
    return any(child.name == "index" for child in tag.children)


def is_array_initialization_block(tag: Tag) -> bool:
    """
    Verifica se um bloco é uma inicialização de array.

    Critérios mais flexíveis:
    1. Tag pai deve ser 'expr'
    2. Tag avô deve ser 'init' OU outro bloco de array
    3. Ou estar dentro de uma estrutura de inicialização
    """
    if not tag.parent:
        return False

    parent = tag.parent
    grandparent = parent.parent if parent else None

    # Caso direto: parent=expr, grandparent=init
    if parent.name == "expr" and grandparent and grandparent.name == "init":
        return True

    # Caso aninhado: dentro de outro bloco de array (arrays multidimensionais)
    if parent.name == "expr" and grandparent and grandparent.name == "block":
        return is_array_initialization_block(grandparent)

    # Caso adicional: pode estar em uma expressão dentro de um bloco
    if parent.name == "expr":
        current = parent
        while current and current.parent:
            current = current.parent
            if current.name == "init":
                return True
            if current.name == "block" and is_array_initialization_block(current):
                return True

    return False


def extract_variable_name(tag: Tag) -> str:
    """Extrai o nome da variável de uma declaração."""
    name_tags = tag.find_children("name")
    if not name_tags:
        return "UNNAMED"

    # Procura pelo primeiro filho 'name' dentro do primeiro 'name'
    var_name_tags = name_tags[0].find_children("name")
    if var_name_tags:
        return var_name_tags[0].text.strip()

    # Fallback: usa o texto direto se não há filhos
    return name_tags[0].text.strip() if name_tags[0].text else "UNNAMED"


def extract_base_type(tag: Tag) -> str:
    """Extrai o tipo base, considerando referências a tipos anteriores."""
    type_tags = tag.find_children("type")
    if not type_tags:
        return "UNKNOWN_TYPE"

    type_tag = type_tags[0]

    # Se tem referência ao tipo anterior
    if type_tag.attrib.get("ref") == "prev":
        return find_previous_decl_type_improved(tag)

    return translate_type(type_tag)


def find_previous_decl_type_improved(tag: Tag) -> str:
    """
    Versão melhorada que funciona corretamente com arrays.

    Procura pela primeira declaração anterior que tem um tipo explícito,
    extraindo o tipo base (sem as dimensões do array).
    """
    parent = tag.parent
    if not parent:
        return "UNKNOWN_TYPE"

    decls = parent.find_children("decl")
    try:
        current_index = decls.index(tag)
    except ValueError:
        return "UNKNOWN_TYPE"

    # Procura declarações anteriores
    for i in range(current_index - 1, -1, -1):
        prev_decl = decls[i]
        type_tags = prev_decl.find_children("type")

        if type_tags and not type_tags[0].attrib.get("ref") == "prev":
            # Encontrou um tipo explícito
            return translate_type(type_tags[0])

    return "UNKNOWN_TYPE"


def build_array_type(tag: Tag, base_type: str, translate_fn) -> str:
    """
    Constrói a representação do tipo array aninhado.

    Exemplo: int[3][2] -> array(3, array(2, int))
    """
    name_tags = tag.find_children("name")
    if not name_tags:
        return base_type

    indices = name_tags[0].find_children("index")
    if not indices:
        return base_type

    # Extrai dimensões
    dimensions = []
    for index in indices:
        dim = extract_array_dimension(index, translate_fn)
        dimensions.append(dim)

    # Constrói tipo aninhado da direita para a esquerda
    result_type = base_type
    for dim in reversed(dimensions):
        result_type = f"array({dim}, {result_type})"

    return result_type


def extract_array_dimension(index_tag: Tag, translate_fn) -> str:
    """
    Extrai a dimensão de um índice de array.

    Retorna:
    - A expressão traduzida se existe
    - "_" se o índice está vazio (array dinâmico)
    """
    expr_tags = index_tag.find_children("expr")
    if expr_tags:
        return translate_fn(expr_tags[0]).strip()
    return "_"


def translate_array_init(init_tag: Tag, translate_fn) -> str:
    expr_tags = init_tag.find_children("expr")
    if not expr_tags:
        return "EMPTY_INIT"

    # Se contiver bloco (ex: {1, 2, 3}), garante que será traduzido corretamente
    expr = expr_tags[0]
    block_tags = expr.find_children("block")
    if block_tags:
        return translate_fn(block_tags[0]).strip()

    return translate_fn(expr).strip()


def translate_base_decl(tag: Tag) -> str:
    """
    Fallback para declarações não-array.
    Evita import circular importando dentro da função.
    """
    from source.xml2clearly.declarations.variables import base
    return base.translate_decl(tag)