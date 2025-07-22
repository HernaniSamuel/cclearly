from source.xml2clearly.xml_manager import generate_tag
from source.xml2clearly.translate import translate

# Carrega o XML gerado pelo srcML
xml = generate_tag("arquivo.c.xml")

# Traduz o nó raiz (ou qualquer tag específica)
saida = translate(xml)

print(saida)
