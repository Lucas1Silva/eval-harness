"""Golden set sintético: fornecedores limpos, ruído e gravação do JSONL.

Níveis de dificuldade:
  0  limpo
  1  caixa aleatória, espaços extras e CNPJ com ou sem pontuação
  2  nível 1 mais ordem trocada, prefixo lixo e cidade/UF colados (às vezes sem acento)
  3  nível 2 mais um distrator numérico (telefone ou CEP) perto do CNPJ e CNPJ alfanumérico

O ruído nunca destrói informação: o gabarito sempre sai da entrada.
"""

import hashlib
import json
import random
from pathlib import Path

from harness import cnpj
from harness.texto import remover_acentos

CIDADES = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Salvador", "BA"), ("Fortaleza", "CE"), ("Recife", "PE"),
    ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Manaus", "AM"),
    ("Belém", "PA"), ("Goiânia", "GO"), ("Campinas", "SP"),
    ("São Luís", "MA"), ("Maceió", "AL"), ("Natal", "RN"),
    ("Teresina", "PI"), ("João Pessoa", "PB"), ("Florianópolis", "SC"),
    ("Vitória", "ES"), ("Cuiabá", "MT"), ("Campo Grande", "MS"),
    ("Aracaju", "SE"), ("Uberlândia", "MG"), ("Londrina", "PR"),
    ("Joinville", "SC"), ("Ribeirão Preto", "SP"), ("Santos", "SP"),
    ("Juiz de Fora", "MG"), ("Sorocaba", "SP"), ("Foz do Iguaçu", "PR"),
]
RAIZES = ["ACME", "BRASIL", "NORDESTE", "ATLANTICO", "PLANALTO", "VALE VERDE",
          "ESTRELA", "HORIZONTE", "CENTRAL", "SUL AMERICA", "PIONEIRA", "UNIAO"]
RAMOS = ["DISTRIB", "COMERCIO", "INDUSTRIA", "LOGISTICA", "SERVICOS",
         "TRANSPORTES", "ALIMENTOS", "MATERIAIS"]
SUFIXOS = ["LTDA", "S.A.", "EPP", "ME"]
PREFIXOS_LIXO = ["FORN.", "CAD:", "FORNECEDOR -", "REG."]
NIVEIS = 4


# --- ruído de texto: (texto, rng) -> texto ---------------------------------

def caixa_aleatoria(texto: str, rng: random.Random) -> str:
    return "".join(rng.choice((c.upper(), c.lower())) for c in texto)


def espacos_extras(texto: str, rng: random.Random) -> str:
    return "".join(" " * rng.randint(1, 3) if c == " " else c for c in texto)


def prefixo_lixo(texto: str, rng: random.Random) -> str:
    return f"{rng.choice(PREFIXOS_LIXO)} {texto}"


# --- geração ---------------------------------------------------------------

def gerar_fornecedor(rng: random.Random, alfanumerico: bool = False) -> dict:
    """Um fornecedor limpo: é o gabarito."""
    cidade, uf = rng.choice(CIDADES)
    return {
        "razao_social": f"{rng.choice(RAIZES)} {rng.choice(RAMOS)} {rng.choice(SUFIXOS)}",
        "cnpj": cnpj.gerar(rng, alfanumerico),
        "cidade": cidade,
        "uf": uf,
    }


def _distrator(rng: random.Random) -> str:
    if rng.random() < 0.5:
        return f"TEL ({rng.randint(11, 99)}) 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"
    return f"CEP {rng.randint(10000, 99999)}-{rng.randint(100, 999)}"


def montar_entrada(fornecedor: dict, nivel: int, rng: random.Random) -> str:
    """Transforma o fornecedor limpo em um texto bagunçado do nível pedido."""
    cidade, uf = fornecedor["cidade"], fornecedor["uf"]
    cnpj_txt = fornecedor["cnpj"]
    if nivel == 0 or rng.random() < 0.5:
        cnpj_txt = cnpj.formatar(cnpj_txt)

    if nivel >= 2:
        if rng.random() < 0.5:
            cidade = remover_acentos(cidade)
        local = f"{cidade}{rng.choice('/-')}{uf}"
    else:
        local = f"{cidade}, {uf}"

    parte_cnpj = f"CNPJ {cnpj_txt}"
    if nivel >= 3:
        parte_cnpj += f" - {_distrator(rng)}"

    partes = [fornecedor["razao_social"], parte_cnpj, local]
    if nivel >= 2:
        rng.shuffle(partes)
    texto = " - ".join(partes)

    if nivel >= 2:
        texto = prefixo_lixo(texto, rng)
    if nivel >= 1:
        texto = espacos_extras(caixa_aleatoria(texto, rng), rng)
    return texto


def gerar_golden(n: int, semente: int) -> list[dict]:
    """n casos com os níveis em rodízio (0, 1, 2, 3, 0, ...)."""
    rng = random.Random(semente)
    casos = []
    for i in range(n):
        nivel = i % NIVEIS
        gabarito = gerar_fornecedor(rng, alfanumerico=nivel == 3)
        casos.append({
            "caso_id": f"c{i + 1:03d}",
            "dificuldade": nivel,
            "entrada": montar_entrada(gabarito, nivel, rng),
            "gabarito": gabarito,
        })
    return casos


def gravar_jsonl(casos: list[dict], caminho: Path) -> str:
    """Grava uma linha por caso (UTF-8, \\n) e devolve o SHA-256 do arquivo."""
    linhas = [json.dumps(c, ensure_ascii=False) for c in casos]
    dados = ("\n".join(linhas) + "\n").encode("utf-8")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(dados)
    return hashlib.sha256(dados).hexdigest()
