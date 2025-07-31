from lxml import etree

NSMAP = {"src": "http://www.srcML.org/srcML/src", "cpp": "http://www.srcML.org/srcML/cpp"}


class Tag:
    def __init__(self, elem, parent=None):
        self.name = etree.QName(elem).localname
        self.attrib = dict(elem.attrib)

        # Extrai posições pos:start e pos:end como tuplas (linha, coluna)
        start_str = self.attrib.get("{http://www.srcML.org/srcML/position}start")
        end_str = self.attrib.get("{http://www.srcML.org/srcML/position}end")

        self.start = tuple(map(int, start_str.split(":"))) if start_str else (float("inf"), float("inf"))
        self.end = tuple(map(int, end_str.split(":"))) if end_str else (float("-inf"), float("-inf"))

        self.text = (elem.text or "").strip()
        self.parent = parent

        # Herda indentação do pai, mas +1 se o pai é um <block>
        if parent:
            self.indent_level = parent.indent_level + 1 if parent.name == "block" else parent.indent_level
        else:
            self.indent_level = 0

        # Constrói filhos com referência ao self como parent
        self.children = [Tag(child, self) for child in elem]

        # Ordena filhos pela posição no código original
        self.children.sort(key=lambda c: c.start)

    def __repr__(self):
        return f"Tag(name={self.name}, indent={self.indent_level}, children={len(self.children)})"

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def find_children(self, name):
        return [c for c in self.children if c.name == name]

    def search(self, path: str):
        parts = path.strip("/").split("/")
        return self._search_path(parts)

    def _search_path(self, parts):
        if not parts:
            return [self]
        next_name = parts[0]
        matches = [child for child in self.children if child.name == next_name]
        results = []
        for match in matches:
            results += match._search_path(parts[1:])
        return results

    def find(self, name: str) -> 'Tag' or None:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def find_text(self, name: str) -> str or None:
        node = self.find(name)
        if node:
            return node.text
        return None


def generate_tag(xml_file):
    tree = etree.parse(xml_file)
    root_tag = Tag(tree.getroot())
    return root_tag
