from source.xml2clearly.registry import register
from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.pointers.resolve import resolve_pointer_notation


def extract_storage_specifiers(type_tag: Tag) -> list:
    """Extrai especificadores de armazenamento como static, extern, etc."""
    if not type_tag:
        return []

    storage_specifiers = {"static", "extern", "register", "auto", "typedef"}
    found_specifiers = []

    # Verifica texto direto
    if type_tag.text and type_tag.text.strip() in storage_specifiers:
        found_specifiers.append(type_tag.text.strip())

    # Verifica filhos
    for child in type_tag.children:
        if child.name == "specifier" and child.text:
            text = child.text.strip()
            if text in storage_specifiers:
                found_specifiers.append(text)

    return found_specifiers


def extract_type_text(type_tag: Tag) -> str:
    """Extrai apenas o tipo, ignorando especificadores de armazenamento como static, extern"""
    if not type_tag:
        return "void"

    # Lista de especificadores de armazenamento para ignorar
    storage_specifiers = {"static", "extern", "register", "auto", "typedef"}

    # Coleta apenas os elementos que são realmente parte do tipo
    type_parts = []

    # Primeiro adiciona o texto direto se não for especificador
    if type_tag.text and type_tag.text.strip():
        text = type_tag.text.strip()
        if text not in storage_specifiers:
            type_parts.append(text)

    # Processa os filhos, separando especificadores do tipo real
    for child in type_tag.children:
        if child.name == "name" and child.text:
            text = child.text.strip()
            if text not in storage_specifiers:
                type_parts.append(text)
        elif child.name == "modifier" and child.text:
            # Modificadores como * são parte do tipo
            type_parts.append(child.text.strip())
        elif child.name == "specifier" and child.text:
            # Ignora especificadores de armazenamento
            text = child.text.strip()
            if text not in storage_specifiers:
                type_parts.append(text)

    # Se não encontrou nada, tenta uma busca mais ampla
    if not type_parts:
        def get_type_text(tag):
            texts = []
            if tag.text and tag.text.strip():
                text = tag.text.strip()
                if text not in storage_specifiers:
                    texts.append(text)
            for child in tag.children:
                if child.name != "specifier" or (child.text and child.text.strip() not in storage_specifiers):
                    texts.extend(get_type_text(child))
            return texts

        type_parts = get_type_text(type_tag)

    result = " ".join(type_parts).strip()
    return result if result else "void"


def extract_parameter_info(param_tag: Tag) -> tuple:
    """Extrai nome e tipo de um parâmetro usando resolução de ponteiros"""
    pname = "_"
    ptype = "void"

    # Procura primeiro em <decl>
    decl = param_tag.find("decl")
    if decl:
        # Tipo dentro de decl (usa resolução de ponteiros)
        type_subtag = decl.find("type")
        if type_subtag:
            ptype = resolve_pointer_notation(type_subtag)

        # Nome dentro de decl
        name_subtag = decl.find("name")
        if name_subtag and name_subtag.text:
            pname = name_subtag.text.strip()
    else:
        # Se não tem decl, procura diretamente no parâmetro
        type_subtag = param_tag.find("type")
        if type_subtag:
            ptype = resolve_pointer_notation(type_subtag)

        name_subtag = param_tag.find("name")
        if name_subtag and name_subtag.text:
            pname = name_subtag.text.strip()

    return pname, ptype


@register("function_decl", priority=10)
def translate_function_decl(tag: Tag) -> str:
    name_tag = tag.find("name")
    name = name_tag.text.strip() if name_tag and name_tag.text else "anon"

    # Usa resolução de ponteiros para o tipo de retorno
    type_tag = tag.find("type")
    return_type = resolve_pointer_notation(type_tag)
    storage_specs = extract_storage_specifiers(type_tag)

    params = []
    param_list = tag.find("parameter_list")
    if param_list:
        for param in param_list.find_children("parameter"):
            pname, ptype = extract_parameter_info(param)
            if pname == "_" and ptype != "void":
                params.append(ptype)
            else:
                params.append(f"{pname}: {ptype}")

    params_str = ", ".join(params)

    storage_prefix = ""
    if storage_specs:
        storage_prefix = " ".join(storage_specs) + " "

    return f"{name}: {storage_prefix}fn({params_str}) -> {return_type}"


@register("function", priority=10)
def translate_function_def(tag: Tag) -> str:
    from source.xml2clearly.translate import translate

    name_tag = tag.find("name")
    name = name_tag.text.strip() if name_tag and name_tag.text else "anon"

    # Usa resolução de ponteiros para o tipo de retorno
    type_tag = tag.find("type")
    return_type = resolve_pointer_notation(type_tag)
    storage_specs = extract_storage_specifiers(type_tag)

    params = []
    param_list = tag.find("parameter_list")
    if param_list:
        for param in param_list.find_children("parameter"):
            pname, ptype = extract_parameter_info(param)
            if pname == "_" and ptype != "void":
                params.append(ptype)
            else:
                params.append(f"{pname}: {ptype}")

    params_str = ", ".join(params)

    storage_prefix = ""
    if storage_specs:
        storage_prefix = " ".join(storage_specs) + " "

    header = f"def {storage_prefix}{name}({params_str}) -> {return_type}:"

    block = tag.find("block")
    if block:
        body_parts = []
        for child in block.children:
            if child.name == "block_content":
                for inner_child in child.children:
                    translated = translate(inner_child)
                    if translated and translated.strip():
                        body_parts.append(translated.strip())
        body = "\n    ".join(body_parts) if body_parts else "pass"
    else:
        body = "pass"

    return f"{header}\n    {body}"


@register("return", priority=10)
def translate_return(tag: Tag) -> str:
    """Traduz statement return"""
    from source.xml2clearly.translate import translate

    expr_tag = tag.find("expr")
    if expr_tag:
        expr_translated = translate(expr_tag)
        return f"return {expr_translated}"
    else:
        return "return"


@register("name", priority=5)
def translate_name(tag: Tag) -> str:
    """Traduz tags <name> simples"""
    return tag.text.strip() if tag.text else ""


@register("operator", priority=5)
def translate_operator(tag: Tag) -> str:
    """Traduz operadores"""
    return tag.text.strip() if tag.text else ""


def lookup_call_type(name: str) -> str:
    # Por enquanto tudo fn
    # No futuro: verifica macro_table, pointer_table etc
    return "fn"


@register("call", priority=10)
def translate_call(tag: Tag) -> str:
    from source.xml2clearly.translate import translate

    # Nome da função/chamada
    name_tag = tag.find("name")
    name = translate(name_tag) if name_tag else "anon"

    # Argumentos
    arg_list = tag.find("argument_list")
    args = []
    if arg_list:
        for arg in arg_list.find_children("argument"):
            args.append(translate(arg))

    args_str = ", ".join(args)

    # Por enquanto tudo é call fn
    call_type = lookup_call_type(name)
    return f"call {call_type} {name}({args_str})"