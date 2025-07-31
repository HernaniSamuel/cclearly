from source.xml2clearly.registry import register
from source.xml2clearly.xml_manager import Tag


@register("include", priority=10)
def translate_include(tag: Tag) -> str:
    file_tag = tag.find_children("file")
    if not file_tag:
        return None  # fallback para tradutores de menor prioridade

    filename = file_tag[0].text.strip()

    if filename.startswith("<") and filename.endswith(">"):
        filename = filename[1:-1]
        return f'@include system("{filename}")'
    elif filename.startswith('"') and filename.endswith('"'):
        filename = filename[1:-1]
        return f'@include local("{filename}")'
    else:
        return f'@include unknown("{filename}")'
