from source.xml2clearly.xml_manager import Tag

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

def translate_init(init_tag: Tag, translate_fn) -> str:
    expr_tag = init_tag.find_children("expr")
    if expr_tag:
        return translate_fn(expr_tag[0]).strip()
    return "EMPTY_INIT"


def extract_text_recursive(tag: Tag) -> str:
    texts = [tag.text] if tag.text else []
    for child in tag.children:
        child_text = extract_text_recursive(child)
        if child_text:
            texts.append(child_text)
    return "".join(texts)
