# source/xml2clearly/pointers/resolve.py
from source.xml2clearly.registry import register
from source.xml2clearly.xml_manager import Tag


def resolve_pointer_notation(type_tag: Tag, ignore_storage_specifiers=True) -> str:
    """
    Resolve tipos com ponteiros para notação ptr(tipo)
    Exemplo: char ** -> ptr(ptr(char))
             int ***** -> ptr(ptr(ptr(ptr(ptr(int)))))
    """
    if not type_tag:
        return "void"

    base_type = ""
    pointer_depth = 0
    storage_specifiers = {"static", "extern", "register", "auto", "typedef"} if ignore_storage_specifiers else set()

    def extract_type_info(tag: Tag):
        nonlocal base_type, pointer_depth

        # Processa texto direto do elemento
        if tag.text and tag.text.strip():
            text = tag.text.strip()
            if text not in storage_specifiers and not base_type:
                base_type = text

        # Processa filhos em ordem
        for child in tag.children:
            if child.name == "modifier" and child.text == "*":
                pointer_depth += 1
            elif child.name == "name" and child.text:
                text = child.text.strip()
                if text not in storage_specifiers and not base_type:
                    base_type = text
            elif child.name == "specifier" and child.text:
                # Ignora especificadores de armazenamento se solicitado
                text = child.text.strip()
                if text not in storage_specifiers and not base_type:
                    base_type = text
            else:
                # Recursivamente processa outros elementos
                extract_type_info(child)

    extract_type_info(type_tag)

    # Se não encontrou tipo base, assume void
    if not base_type:
        base_type = "void"

    # Aplica os ponteiros de dentro para fora
    result_type = base_type
    for _ in range(pointer_depth):
        result_type = f"ptr({result_type})"

    return result_type


@register("type", priority=100)  # prioridade mais alta que outros tradutores
def resolve_pointer_type(tag: Tag) -> str:
    """Tradutor principal para tipos com ponteiros"""
    return resolve_pointer_notation(tag, ignore_storage_specifiers=True)


@register("decl", priority=15)  # prioridade alta para sobrescrever o tradutor base
def translate_pointer_decl(tag: Tag) -> str:
    """Traduz declarações de variáveis com ponteiros"""

    # Nome da variável
    name_tags = tag.find_children("name")
    var_name = name_tags[0].text.strip() if name_tags else "UNNAMED"

    # Tipo da variável (incluindo ponteiros)
    type_tags = tag.find_children("type")
    if type_tags:
        type_str = resolve_pointer_notation(type_tags[0])
    else:
        type_str = "void"

    # Verifica se há inicialização
    init_tags = tag.find_children("init")
    if init_tags:
        from source.xml2clearly.translate import translate
        init_str = translate(init_tags[0])
        return f"{var_name}: {type_str} = {init_str}"
    else:
        return f"{var_name}: {type_str}"


@register("decl_stmt", priority=15)  # prioridade alta
def translate_pointer_decl_stmt(tag: Tag) -> str:
    """Traduz statements de declaração com ponteiros"""
    from source.xml2clearly.translate import translate

    decls = tag.find_children("decl")
    parts = []

    for decl in decls:
        translated = translate(decl)
        if translated and translated.strip():
            parts.append(translated.strip())

    return ", ".join(parts) if parts else ""


# Função helper para uso em outros módulos
def get_pointer_type(type_tag: Tag) -> str:
    """Função utilitária para obter tipo com ponteiros resolvidos"""
    return resolve_pointer_notation(type_tag)