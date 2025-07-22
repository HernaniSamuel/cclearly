from source.xml2clearly.xml_manager import Tag

# Dicionário que associa cada nome de tag a uma função de tradução
TRANSLATORS = {}

def register(tag_name):
    """Decorador para registrar funções de tradução"""
    def wrapper(func):
        TRANSLATORS[tag_name] = func
        return func
    return wrapper

def translate(tag: Tag) -> str:
    # Procura função registrada para a tag
    handler = TRANSLATORS.get(tag.name)

    if handler:
        return handler(tag)
    else:
        # Se não tem handler específico, traduz filhos
        return "".join(translate(child) for child in tag.children)



# IMPORTS para registrar tradutores implementados em outros arquivos
from source.xml2clearly.declarations import comments
from source.xml2clearly.declarations import variables
