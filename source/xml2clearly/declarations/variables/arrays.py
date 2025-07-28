from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.registry import register

@register("decl", priority=20)
def translate_decl_array(tag: Tag) -> str:
    from source.xml2clearly.translate import translate
    from source.xml2clearly.declarations.variables.helpers import translate_type

    if not is_array_tag(tag):
        return translate_base_decl(tag)

    # Extrair nome e dimensões
    name_tag = tag.find_children("name")[0]
    var_name_tag = name_tag.find_children("name")[0]
    var_name = var_name_tag.text.strip()

    # Extrair tipo base
    type_tag = tag.find_children("type")[0]
    base_type = translate_type(type_tag)

    # Extrair índices e construir array(..., tipo)
    indices = name_tag.find_children("index")
    dims = [translate(index.find_children("expr")[0]) for index in indices]

    array_type = base_type
    for dim in reversed(dims):
        array_type = f"array({dim}, {array_type})"

    return f"{var_name}: {array_type}"

def is_array_tag(tag: Tag) -> bool:
    for name_tag in tag.find_children("name"):
        for child in name_tag.children:
            if isinstance(child, Tag) and child.name == "index":
                return True
    return False

def translate_base_decl(tag: Tag) -> str:
    # aqui, para evitar ciclo, importe dentro da função
    from source.xml2clearly.declarations.variables import base
    return base.translate_decl(tag)
