import random

import pytest

from harness.cnpj import calcular_dv, formatar, gerar, validar


# --- exemplos conhecidos -------------------------------------------------

def test_exemplo_oficial_da_receita_alfanumerico():
    # exemplo do documento de perguntas e respostas da Receita Federal
    assert calcular_dv("12ABC34501DE") == "35"
    assert validar("12.ABC.345/01DE-35")


def test_exemplo_classico_numerico():
    assert validar("11.222.333/0001-81")


def test_dv_errado_e_rejeitado():
    assert not validar("11.222.333/0001-82")


@pytest.mark.parametrize("entrada", ["", "123", "11.222.333/0001-8X", "12.ABC.345/01DE-3!"])
def test_entradas_malformadas_nao_quebram(entrada):
    assert validar(entrada) is False


def test_formatar():
    assert formatar("12abc34501de35") == "12.ABC.345/01DE-35"


# --- propriedades do gerador ---------------------------------------------

@pytest.mark.parametrize("alfanumerico", [False, True])
def test_todo_cnpj_gerado_e_valido(alfanumerico):
    rng = random.Random(42)
    for _ in range(1_000):
        assert validar(gerar(rng, alfanumerico))


def test_mesma_semente_gera_mesmos_cnpjs():
    rng_a = random.Random(7)
    rng_b = random.Random(7)
    lote_a = [gerar(rng_a, True) for _ in range(50)]
    lote_b = [gerar(rng_b, True) for _ in range(50)]
    assert lote_a == lote_b


def test_numerico_nunca_tem_letra():
    rng = random.Random(1)
    assert all(gerar(rng).isdigit() for _ in range(1_000))


# --- limite conhecido do algoritmo ----------------------------------------

def test_ponto_cego_troca_de_6_por_A_nao_e_detectada():
    # '6' vale 6 e 'A' vale 17: diferença de 11.
    # Como o DV é "soma módulo 11", somar 11 x peso não muda o resto,
    # então os dois CNPJs têm o mesmo DV e ambos passam na validação.
    assert validar("61.222.333/0001-50")
    assert validar("A1.222.333/0001-50")
