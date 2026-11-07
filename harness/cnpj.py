"""Geração e validação de CNPJ, numérico e alfanumérico.

Regras da Receita Federal (CNPJ alfanumérico, em vigor desde jul/2026):
- 14 caracteres: 8 de raiz + 4 de ordem (filial) + 2 dígitos verificadores (DV)
- os 12 primeiros podem ser 0-9 ou A-Z; os 2 DVs são sempre 0-9
- cada caractere vale (código ASCII - 48): '0'..'9' -> 0..9, 'A'..'Z' -> 17..42
- cada DV é calculado por módulo 11
"""

import random
import string

PESOS_DV1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
PESOS_DV2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

DIGITOS = string.digits
ALFANUMERICOS = string.digits + string.ascii_uppercase


def _valor(caractere: str) -> int:
    return ord(caractere) - 48


def _digito(base: str, pesos: list[int]) -> str:
    soma = sum(_valor(c) * p for c, p in zip(base, pesos, strict=True))
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def calcular_dv(base12: str) -> str:
    """Recebe os 12 primeiros caracteres e devolve os 2 dígitos verificadores."""
    if len(base12) != 12 or any(c not in ALFANUMERICOS for c in base12):
        raise ValueError(f"base inválida: {base12!r}")
    dv1 = _digito(base12, PESOS_DV1)
    dv2 = _digito(base12 + dv1, PESOS_DV2)
    return dv1 + dv2


def limpar(cnpj: str) -> str:
    """Remove pontuação e espaços e põe em maiúsculas: '12.abc.345/01de-35' -> '12ABC34501DE35'."""
    return "".join(c for c in cnpj.upper() if c not in "./- ")


def validar(cnpj: str) -> bool:
    c = limpar(cnpj)
    if len(c) != 14 or not c[12:].isdigit():
        return False
    try:
        return calcular_dv(c[:12]) == c[12:]
    except ValueError:
        return False


def formatar(cnpj: str) -> str:
    c = limpar(cnpj)
    return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"


def gerar(rng: random.Random, alfanumerico: bool = False) -> str:
    """Gera um CNPJ válido de matriz (ordem 0001), sem pontuação.

    Recebe o gerador aleatório de fora para que a mesma semente
    produza sempre o mesmo golden set.
    """
    alfabeto = ALFANUMERICOS if alfanumerico else DIGITOS
    raiz = "".join(rng.choice(alfabeto) for _ in range(8))
    base = raiz + "0001"
    return base + calcular_dv(base)
