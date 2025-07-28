from source.xml2clearly.registry import register


@register("comment", priority=10)
def translate_comment(tag):
    indent = "    " * tag.indent_level
    text = tag.text  # pode conter múltiplas linhas, e já inclui os delimitadores // ou /* */

    # Dividir em linhas para aplicar indentação em todas
    lines = text.splitlines()

    # Aplicar indent em todas as linhas do comentário
    indented_lines = [indent + line for line in lines]

    # Juntar com nova linha
    return "\n".join(indented_lines)
