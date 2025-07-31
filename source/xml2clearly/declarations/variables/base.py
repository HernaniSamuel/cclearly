from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.registry import register
from source.xml2clearly.declarations.variables.helpers import (
    translate_type,
    find_previous_decl_type,
    translate_init,
    extract_text_recursive,
)


@register("decl_stmt", priority=10)
def translate_decl_stmt(tag: Tag) -> str:
    from source.xml2clearly.translate import translate  # import tardio para quebrar ciclo

    decls = tag.find_children("decl")
    parts = [translate(decl) for decl in decls if translate(decl).strip()]
    return ", ".join(parts)


@register("decl", priority=10)
def translate_decl(tag: Tag) -> str:
    from source.xml2clearly.translate import translate  # import tardio pra evitar circular import

    var_name_tag = tag.find_children("name")
    var_name = var_name_tag[0].text if var_name_tag else "UNNAMED"

    type_tag = tag.find_children("type")
    if type_tag and not type_tag[0].attrib.get("ref") == "prev":
        type_str = translate_type(type_tag[0])
    else:
        type_str = find_previous_decl_type(tag)

    init_tag = tag.find_children("init")
    if init_tag:
        init_str = translate_init(init_tag[0], translate)  # <<-- passa a função translate aqui!
        return f"{var_name}: {type_str} = {init_str}"
    else:
        return f"{var_name}: {type_str}"


@register("expr", priority=10)
def translate_expr(tag: Tag) -> str:
    """Traduz expressões de forma mais inteligente"""
    from source.xml2clearly.translate import translate

    # Se a expressão tem filhos, processa cada um
    if tag.children:
        parts = []
        for child in tag.children:
            translated = translate(child)
            if translated and translated.strip():
                parts.append(translated.strip())

        # Junta com espaços apropriados
        result = " ".join(parts)
        return result if result else extract_text_recursive(tag)
    else:
        # Se não tem filhos, usa o texto direto
        return tag.text.strip() if tag.text else ""


@register("literal", priority=10)
def translate_literal(tag: Tag) -> str:
    return tag.text.strip() if tag.text else ""


@register("comment", priority=10)
def translate_comment(tag: Tag) -> str:
    """Traduz comentários preservando o formato original"""
    comment_type = tag.attrib.get("type", "")

    if comment_type == "line":
        # Comentário de linha //
        return f"# {tag.text.strip()}" if tag.text else ""
    elif comment_type == "block":
        # Comentário de bloco /* */
        lines = tag.text.strip().split('\n') if tag.text else [""]
        if len(lines) == 1:
            return f"# {lines[0].strip()}"
        else:
            # Comentário multi-linha
            result = ['"""']
            for line in lines:
                result.append(line.strip())
            result.append('"""')
            return '\n'.join(result)

    return ""


@register("block_content", priority=10)
def translate_block_content(tag: Tag) -> str:
    """Traduz conteúdo de blocos"""
    from source.xml2clearly.translate import translate

    parts = []
    for child in tag.children:
        translated = translate(child)
        if translated and translated.strip():
            parts.append(translated.strip())

    return "\n".join(parts) if parts else ""