"""Inicialização do pacote CB2325NumericaG07:"""
from importlib.metadata import PackageNotFoundError, version

#submodulos
from . import erros, aproximacao, integracao, interpolacao, raizes

__all__ = ["erros", "aproximacao", "integracao", "interpolacao", "raizes"]

#tenta buscar a versão do pacote, se não conseguir, define como 0.0.0
try:
    __version__ = version("CB2325NumericaG07")
except PackageNotFoundError:
    __version__ = "0.0.0"