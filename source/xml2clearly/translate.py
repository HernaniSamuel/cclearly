from source.xml2clearly.xml_manager import Tag
from source.xml2clearly.registry import TRANSLATORS
from source.xml2clearly.declarations import comments, variables, functions
from source.xml2clearly.directives import include, macros  # garante o registro
from source.xml2clearly.pointers import resolve  # garante o registro dos tradutores de ponteiros

def compute_spacing(prev_end, curr_start):
    prev_line, prev_col = prev_end
    curr_line, curr_col = curr_start

    if curr_line == prev_line:
        return " " * max(1, curr_col - prev_col)
    else:
        return "\n" * max(1, curr_line - prev_line)

def translate(tag: Tag) -> str:
    translators = TRANSLATORS.get(tag.name, [])

    for _, func in translators:
        result = func(tag)
        if result is not None:
            return result

    # fallback genérico com espaçamento proporcional
    result = []
    prev_end = None

    for child in tag.children:
        spacing = ""
        if prev_end and hasattr(child, "start"):
            spacing = compute_spacing(prev_end, child.start)

        result.append(spacing + translate(child))

        end_str = child.attrib.get("{http://www.srcML.org/srcML/position}end")
        if end_str:
            prev_end = tuple(map(int, end_str.split(":")))

    return "".join(result)