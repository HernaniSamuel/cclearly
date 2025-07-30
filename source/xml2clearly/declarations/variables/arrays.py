from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.registry import register
from source.xml2clearly.declarations.variables.helpers import translate_type


# =============================================================================
# CONFIGURAÇÕES SIMPLES (opcional)
# =============================================================================

class ArrayConfig:
    """Configurações básicas para arrays."""
    UNKNOWN_DIM = "_"
    UNNAMED_VAR = "UNNAMED"
    UNKNOWN_TYPE = "UNKNOWN_TYPE"


config = ArrayConfig()


# =============================================================================
# FUNÇÕES AUXILIARES MELHORADAS
# =============================================================================

def safe_get_text(tag: Tag, default: str = "") -> str:
    """Pega texto de forma segura."""
    return tag.text.strip() if tag.text else default


def find_tag_by_name(tag: Tag, name: str) -> Tag | None:
    """Encontra primeira tag filha com nome específico."""
    return next((child for child in tag.children
                 if hasattr(child, 'name') and child.name == name), None)


def has_any_index(tag: Tag) -> bool:
    """Verifica se tem algum índice em qualquer lugar."""
    if hasattr(tag, 'name') and tag.name == "index":
        return True
    if hasattr(tag, 'children'):
        return any(has_any_index(child) for child in tag.children)
    return False


# =============================================================================
# MELHORIAS NO CÓDIGO ORIGINAL
# =============================================================================

@register("decl", priority=20)
def translate_decl_array(tag: Tag) -> str:
    """
    Traduz declarações de arrays com melhor tratamento de erros.
    """
    from source.xml2clearly.translate import translate

    try:
        if not is_array_tag(tag):
            return translate_base_decl(tag)

        # Extrair informações básicas
        var_name = extract_variable_name(tag)
        base_type = extract_base_type(tag)
        array_type = build_array_type(tag, base_type, translate)

        # Verificar se há inicialização
        init_tags = tag.find_children("init")
        if init_tags:
            init_str = translate_array_init(init_tags[0], translate)
            return f"{var_name}: {array_type} = {init_str}"
        else:
            return f"{var_name}: {array_type}"

    except Exception:
        # Em caso de erro, tenta tradução base
        return translate_base_decl(tag)


@register("block", priority=60)
def translate_indexed_array_block(tag: Tag) -> str | None:
    """
    Traduz blocos indexados com detecção melhorada.
    Corrige atribuições sequenciais para evitar sobrescrever índices explícitos.
    """
    from source.xml2clearly.translate import translate
    if not is_indexed_array_block(tag):
        return None

    try:
        var_name = infer_variable_name(tag) or "?"
        items = []
        used_index_keys = set()
        sequential_index = 0

        # Primeiro, adiciona todos os índices explícitos
        for expr in tag.find_children("expr"):
            if has_any_index(expr):
                index_tag = next((n for n in expr.walk() if getattr(n, 'name', None) == "index"), None)
                index_expr = find_tag_by_name(index_tag, "expr") if index_tag else None
                if index_expr:
                    index_str = translate(index_expr).strip()
                    value_str = None

                    found_eq = False
                    for child in expr.children:
                        if getattr(child, 'name', None) == "operator" and getattr(child, 'text', '') == "=":
                            found_eq = True
                        elif found_eq and getattr(child, 'name', None) == "literal":
                            value_str = translate(child).strip()
                            break

                    if value_str:
                        used_index_keys.add(index_str)
                        items.append(f"{var_name}[{index_str}] = {value_str}")

        # Agora, adiciona os valores que não têm índice explícito
        for expr in tag.find_children("expr"):
            if not has_any_index(expr):
                for child in expr.children:
                    if getattr(child, 'name', None) == "literal":
                        value_str = translate(child).strip()

                        # pula índices já usados
                        while str(sequential_index) in used_index_keys:
                            sequential_index += 1

                        items.append(f"{var_name}[{sequential_index}] = {value_str}")
                        used_index_keys.add(str(sequential_index))
                        sequential_index += 1
                        break

        return "(" + ", ".join(items) + ")"

    except Exception:
        import traceback
        traceback.print_exc()
        return None


def extract_index_int(expr: Tag, translate_fn) -> int | None:
    """Extrai valor inteiro do índice, se possível."""
    index_tag = next((n for n in expr.walk() if getattr(n, 'name', None) == "index"), None)
    index_expr = find_tag_by_name(index_tag, "expr") if index_tag else None
    if index_expr:
        try:
            return int(translate_fn(index_expr).strip())
        except (ValueError, TypeError):
            return None
    return None

@register("block", priority=50)
def translate_array_block(tag: Tag) -> str | None:
    """
    Traduz blocos sequenciais com melhor recursão.
    """
    from source.xml2clearly.translate import translate

    if not is_array_initialization_block(tag):
        return None

    try:
        return translate_block_recursive(tag, translate)
    except Exception:
        return None


# =============================================================================
# FUNÇÕES AUXILIARES MELHORADAS
# =============================================================================

def parse_indexed_expression(expr: Tag, var_name: str, translate_fn) -> str | None:
    """
    Extrai item de expressão indexada de forma mais robusta.
    """
    try:
        # Verifica se tem index (elemento indexado)
        index_tag = None
        for node in expr.walk():
            if hasattr(node, 'name') and node.name == "index":
                index_tag = node
                break

        if index_tag:
            # Elemento indexado: [i] = valor
            index_expr = find_tag_by_name(index_tag, "expr")
            index_str = translate_fn(index_expr).strip() if index_expr else "_"

            # Procura o valor após o operador =
            # O valor vem depois do index na estrutura XML
            value_str = None
            found_operator = False

            for child in expr.children:
                if hasattr(child, 'name'):
                    if child.name == "operator" and hasattr(child, 'text') and child.text == "=":
                        found_operator = True
                    elif found_operator and child.name == "literal":
                        value_str = translate_fn(child).strip()
                        break

            if value_str:
                return f"{var_name}[{index_str}] = {value_str}"
        else:
            # Elemento sequencial - procura literal diretamente
            for child in expr.children:
                if hasattr(child, 'name') and child.name == "literal":
                    value_str = translate_fn(child).strip()
                    return f"{var_name}[?] = {value_str}"

    except Exception:
        pass

    return None


def translate_block_recursive(block_tag: Tag, translate_fn) -> str:
    """
    Traduz bloco recursivamente de forma mais limpa.
    """
    elements = []

    for child in block_tag.children:
        if hasattr(child, 'name') and child.name == "expr":
            element = translate_expression_content(child, translate_fn)
            if element:
                elements.append(element)

    return "[" + ", ".join(elements) + "]"


def translate_expression_content(expr_tag: Tag, translate_fn) -> str | None:
    """
    Traduz conteúdo de expressão (bloco ou valor).
    """
    # Procura primeiro por blocos aninhados
    block_tag = find_tag_by_name(expr_tag, "block")
    if block_tag:
        return translate_block_recursive(block_tag, translate_fn)

    # Senão, traduz a expressão diretamente
    return translate_fn(expr_tag).strip()


def is_array_tag(tag: Tag) -> bool:
    """Verifica se é declaração de array (versão mais robusta)."""
    try:
        name_tags = tag.find_children("name")
        return any(has_index_children(name) for name in name_tags)
    except Exception:
        return False


def has_index_children(tag: Tag) -> bool:
    """Verifica se tem filhos index."""
    try:
        return any(hasattr(child, 'name') and child.name == "index"
                   for child in tag.children)
    except Exception:
        return False


def is_indexed_array_block(tag: Tag) -> bool:
    """Detecta blocos indexados de forma mais simples."""
    try:
        for expr in tag.find_children("expr"):
            if has_any_index(expr):
                return True
        return False
    except Exception:
        return False


def is_array_initialization_block(tag: Tag) -> bool:
    """
    Detecta blocos de inicialização (versão mais precisa).
    """
    try:
        if not tag.parent:
            return False

        parent = tag.parent
        grandparent = parent.parent if parent else None

        # Caso direto: parent=expr, grandparent=init
        if (hasattr(parent, 'name') and parent.name == "expr" and
                hasattr(grandparent, 'name') and grandparent and grandparent.name == "init"):
            return True

        # Caso aninhado: dentro de outro bloco de array (arrays multidimensionais)
        if (hasattr(parent, 'name') and parent.name == "expr" and
                hasattr(grandparent, 'name') and grandparent and grandparent.name == "block"):
            return is_array_initialization_block(grandparent)

        return False
    except Exception:
        return False


def extract_variable_name(tag: Tag) -> str:
    """Extrai nome com fallbacks."""
    try:
        name_tags = tag.find_children("name")
        if not name_tags:
            return config.UNNAMED_VAR

        # Tenta primeiro filho name
        inner_names = name_tags[0].find_children("name")
        if inner_names:
            return safe_get_text(inner_names[0], config.UNNAMED_VAR)

        # Fallback para texto direto
        return safe_get_text(name_tags[0], config.UNNAMED_VAR)

    except Exception:
        return config.UNNAMED_VAR


def extract_base_type(tag: Tag) -> str:
    """Extrai tipo base com cache simples."""
    try:
        type_tags = tag.find_children("type")
        if not type_tags:
            return config.UNKNOWN_TYPE

        type_tag = type_tags[0]

        # Se referencia tipo anterior
        if type_tag.attrib.get("ref") == "prev":
            return find_previous_type(tag)

        return translate_type(type_tag)

    except Exception:
        return config.UNKNOWN_TYPE


def find_previous_type(tag: Tag) -> str:
    """Encontra tipo anterior (versão mais simples)."""
    try:
        parent = tag.parent
        if not parent:
            return config.UNKNOWN_TYPE

        decls = parent.find_children("decl")
        current_idx = decls.index(tag) if tag in decls else -1

        # Procura declaração anterior com tipo explícito
        for i in range(current_idx - 1, -1, -1):
            prev_decl = decls[i]
            type_tags = prev_decl.find_children("type")

            if type_tags and type_tags[0].attrib.get("ref") != "prev":
                return translate_type(type_tags[0])

        return config.UNKNOWN_TYPE

    except Exception:
        return config.UNKNOWN_TYPE


def infer_variable_name(tag: Tag) -> str | None:
    """Infere nome da variável (versão simplificada)."""
    try:
        current = tag
        # Sobe até encontrar decl
        while current and not (hasattr(current, 'name') and current.name == "decl"):
            current = current.parent

        if current:
            return extract_variable_name(current)

    except Exception:
        pass

    return None


def build_array_type(tag: Tag, base_type: str, translate_fn) -> str:
    """Constrói tipo array (versão mais robusta)."""
    try:
        name_tags = tag.find_children("name")
        if not name_tags:
            return base_type

        indices = name_tags[0].find_children("index")
        if not indices:
            return base_type

        # Constrói tipo da direita para esquerda
        result_type = base_type
        for index in reversed(indices):
            dim = extract_array_dimension(index, translate_fn)
            result_type = f"array({dim}, {result_type})"

        return result_type

    except Exception:
        return base_type


def extract_array_dimension(index_tag: Tag, translate_fn) -> str:
    """Extrai dimensão do array."""
    try:
        expr_tags = index_tag.find_children("expr")
        if expr_tags:
            return translate_fn(expr_tags[0]).strip()
    except Exception:
        pass

    return config.UNKNOWN_DIM


def translate_array_init(init_tag: Tag, translate_fn) -> str:
    """Traduz inicialização."""
    try:
        expr_tags = init_tag.find_children("expr")
        if not expr_tags:
            return "[]"

        expr = expr_tags[0]
        block_tags = expr.find_children("block")
        if block_tags:
            return translate_fn(block_tags[0]).strip()

        return translate_fn(expr).strip()

    except Exception:
        return "[]"


def translate_base_decl(tag: Tag) -> str:
    """Fallback para declarações não-array."""
    try:
        from source.xml2clearly.declarations.variables import base
        return base.translate_decl(tag)
    except Exception:
        return "TRANSLATION_ERROR"

