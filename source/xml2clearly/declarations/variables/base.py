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
    return extract_text_recursive(tag)

@register("literal", priority=10)
def translate_literal(tag: Tag) -> str:
    return tag.text or ""
