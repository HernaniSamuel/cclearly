from source.xml2clearly.translate import register, translate
from source.xml2clearly.xml_manager import Tag

@register("decl_stmt")
def translate_decl_stmt(tag: Tag) -> str:
    lines = []
    for decl in tag.find_children("decl"):
        line = translate(decl)
        if line.strip():
            lines.append(line)
    return "\n".join(lines) + "\n"

@register("decl")
def translate_decl(tag: Tag) -> str:
    var_name_tag = tag.find_children("name")
    var_name = var_name_tag[0].text if var_name_tag else "UNNAMED"

    type_tag = tag.find_children("type")
    if type_tag and not type_tag[0].attrib.get("ref") == "prev":
        type_str = translate_type(type_tag[0])
    else:
        type_str = find_previous_decl_type(tag)

    init_tag = tag.find_children("init")
    if init_tag:
        init_str = translate_init(init_tag[0])
        return f"{var_name}: {type_str} = {init_str}"
    else:
        return f"{var_name}: {type_str}"

def find_previous_decl_type(tag: Tag) -> str:
    parent = tag.parent
    if not parent:
        return "UNKNOWN_TYPE"
    decls = parent.find_children("decl")
    try:
        index = decls.index(tag)
    except ValueError:
        return "UNKNOWN_TYPE"
    for i in range(index - 1, -1, -1):
        t = decls[i].find_children("type")
        if t and not t[0].attrib.get("ref") == "prev":
            return translate_type(t[0])
    return "UNKNOWN_TYPE"

def translate_type(type_tag: Tag) -> str:
    parts = []

    def extract_type_parts(tag: Tag):
        if tag.name in ("specifier", "name", "modifier"):
            if tag.children:
                for child in tag.children:
                    extract_type_parts(child)
            if tag.text:
                parts.append(tag.text)
        else:
            if tag.text:
                parts.append(tag.text)
            for child in tag.children:
                extract_type_parts(child)

    extract_type_parts(type_tag)
    return " ".join(parts).strip() or "UNKNOWN_TYPE"

def translate_init(init_tag: Tag) -> str:
    expr_tag = init_tag.find_children("expr")
    if expr_tag:
        return translate(expr_tag[0]).strip()
    return "EMPTY_INIT"

def extract_text_recursive(tag: Tag) -> str:
    texts = [tag.text] if tag.text else []
    for child in tag.children:
        child_text = extract_text_recursive(child)
        if child_text:
            texts.append(child_text)
    return "".join(texts)

@register("expr")
def translate_expr(tag: Tag) -> str:
    return extract_text_recursive(tag)

@register("literal")
def translate_literal(tag: Tag) -> str:
    return tag.text or ""
