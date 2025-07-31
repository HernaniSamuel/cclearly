# source/xml2clearly/pointers/__init__.py

# Importa o módulo de resolução para registrar os tradutores
from . import resolve

# Exporta função utilitária
from .resolve import get_pointer_type, resolve_pointer_notation

__all__ = ['get_pointer_type', 'resolve_pointer_notation']