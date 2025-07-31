from source.xml2clearly.registry import register
from source.xml2clearly.xml_manager import Tag


@register("define", priority=10)
def translate_macro_flag(tag: Tag) -> str:
    macro_tag = tag.find_children("macro")
    if not macro_tag:
        return None

    name_tag = macro_tag[0].find_children("name")
    value_tag = macro_tag[0].find_children("value")

    if name_tag and not value_tag:
        name = name_tag[0].text.strip()
        return f'@macro flag("{name}")'

    return None

