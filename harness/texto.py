import unicodedata


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def normalizar(texto: str) -> str:
    """Maiúsculas, sem acento e com espaços colapsados."""
    return " ".join(remover_acentos(texto).upper().split())
