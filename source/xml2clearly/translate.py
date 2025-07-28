from source.xml2clearly.xml_manager import Tag

# Dicionário que associa cada nome de tag a uma função de tradução
TRANSLATORS = {}

def compute_spacing(prev_end, curr_start):
    prev_line, prev_col = prev_end
    curr_line, curr_col = curr_start

    line_diff = curr_line - prev_line
    same_line = line_diff == 0

    if same_line:
        # Espaço proporcional à diferença de colunas
        space = " " * max(1, curr_col - prev_col)
        return space
    else:
        # Nova linha proporcional ao número de linhas de diferença
        lines = "\n" * max(1, line_diff)
        return lines


def register(tag_name):
    """Decorador para registrar funções de tradução"""
    def wrapper(func):
        TRANSLATORS[tag_name] = func
        return func
    return wrapper

def translate(tag: Tag) -> str:
    handler = TRANSLATORS.get(tag.name)
    if handler:
        return handler(tag)

    # tradução genérica com espaçamento proporcional
    result = []
    prev_end = None

    for child in tag.children:
        spacing = ""
        if prev_end:
            spacing = compute_spacing(prev_end, child.start)

        result.append(spacing + translate(child))
        # salva o end atual para usar na próxima iteração
        end_str = child.attrib.get("{http://www.srcML.org/srcML/position}end")
        if end_str:
            prev_end = tuple(map(int, end_str.split(":")))

    return "".join(result)



# IMPORTS para registrar tradutores implementados em outros arquivos
from source.xml2clearly.declarations import comments
from source.xml2clearly.declarations import variables
