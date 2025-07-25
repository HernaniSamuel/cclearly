from lxml import etree

NSMAP = {"src": "http://www.srcML.org/srcML/src", "cpp": "http://www.srcML.org/srcML/cpp"}


class Tag:
    def __init__(self, elem, parent=None):
        self.name = etree.QName(elem).localname
        self.attrib = dict(elem.attrib)
        self.text = (elem.text or "").strip()
        self.parent = parent

        # Herda indentação do pai, mas +1 se o pai é um <block>
        if parent:
            self.indent_level = parent.indent_level + 1 if parent.name == "block" else parent.indent_level
        else:
            self.indent_level = 0

        # Constrói filhos com referência ao self como parent
        self.children = [Tag(child, self) for child in elem]

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

def generate_tag(xml_file):
    tree = etree.parse(xml_file)
    root_tag = Tag(tree.getroot())
    return root_tag
