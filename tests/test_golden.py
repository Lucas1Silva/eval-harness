import hashlib
import json
import random
import re

from harness import cnpj, golden
from harness.cli import main
from harness.texto import normalizar, remover_acentos

CASOS = golden.gerar_golden(40, 42)


def test_remover_acentos_e_normalizar():
    assert remover_acentos("São Luís") == "Sao Luis"
    assert normalizar("  são   paulo ") == "SAO PAULO"


def test_cidades_embutidas():
    assert len(golden.CIDADES) == 30
    assert any(remover_acentos(c) != c for c, _ in golden.CIDADES)


def test_gerar_fornecedor_e_limpo_e_valido():
    f = golden.gerar_fornecedor(random.Random(1))
    assert cnpj.validar(f["cnpj"]) and f["cnpj"].isdigit()
    assert (f["cidade"], f["uf"]) in golden.CIDADES
    assert f["razao_social"] == f["razao_social"].upper()


def test_gerar_fornecedor_alfanumerico():
    rng = random.Random(3)
    cnpjs = [golden.gerar_fornecedor(rng, alfanumerico=True)["cnpj"] for _ in range(20)]
    assert all(cnpj.validar(c) for c in cnpjs)
    assert any(not c.isdigit() for c in cnpjs)


def test_caixa_aleatoria_preserva_conteudo_e_e_deterministica():
    a = golden.caixa_aleatoria("Acme Ltda", random.Random(5))
    assert normalizar(a) == "ACME LTDA"
    assert a == golden.caixa_aleatoria("Acme Ltda", random.Random(5))


def test_espacos_extras_preserva_conteudo():
    t = golden.espacos_extras("a b c", random.Random(5))
    assert normalizar(t) == "A B C"
    assert t != "a b c"


def test_prefixo_lixo():
    t = golden.prefixo_lixo("ACME", random.Random(5))
    assert t.endswith(" ACME") and t.split()[0] != "ACME"


def test_montar_entrada_nivel_0_e_limpo():
    f = {"razao_social": "ACME DISTRIB LTDA", "cnpj": "11222333000181",
         "cidade": "Recife", "uf": "PE"}
    t = golden.montar_entrada(f, 0, random.Random(1))
    assert t == "ACME DISTRIB LTDA - CNPJ 11.222.333/0001-81 - Recife, PE"


def test_gerar_golden_formato():
    assert len(CASOS) == 40
    assert [c["caso_id"] for c in CASOS[:2]] == ["c001", "c002"]
    for c in CASOS:
        assert set(c) == {"caso_id", "dificuldade", "entrada", "gabarito"}
        assert set(c["gabarito"]) == {"razao_social", "cnpj", "cidade", "uf"}


def test_todo_gabarito_tem_cnpj_valido_sem_pontuacao():
    for c in CASOS:
        cnpj_gab = c["gabarito"]["cnpj"]
        assert cnpj.validar(cnpj_gab)
        assert cnpj_gab == cnpj.limpar(cnpj_gab)


def test_todos_os_niveis_aparecem():
    assert {c["dificuldade"] for c in CASOS} == {0, 1, 2, 3}


def test_nivel_3_tem_cnpj_alfanumerico_e_distrator():
    nivel3 = [c for c in CASOS if c["dificuldade"] == 3]
    assert any(not c["gabarito"]["cnpj"].isdigit() for c in nivel3)
    assert all("TEL" in c["entrada"].upper() or "CEP" in c["entrada"].upper() for c in nivel3)


def test_cada_campo_do_gabarito_aparece_na_entrada():
    for c in CASOS:
        g = c["gabarito"]
        entrada = normalizar(c["entrada"])
        assert normalizar(g["razao_social"]) in entrada, c
        assert normalizar(g["cidade"]) in entrada, c
        assert re.search(rf"(?<![A-Z]){g['uf']}(?![A-Z])", entrada), c
        assert g["cnpj"] in cnpj.limpar(c["entrada"]), c


def test_mesma_semente_gera_o_mesmo_hash(tmp_path):
    h1 = golden.gravar_jsonl(golden.gerar_golden(40, 42), tmp_path / "a.jsonl")
    h2 = golden.gravar_jsonl(golden.gerar_golden(40, 42), tmp_path / "b.jsonl")
    h3 = golden.gravar_jsonl(golden.gerar_golden(40, 43), tmp_path / "c.jsonl")
    assert h1 == h2
    assert h1 != h3


def test_gravar_jsonl_uma_linha_por_caso_e_hash_do_arquivo(tmp_path):
    caminho = tmp_path / "g.jsonl"
    h = golden.gravar_jsonl(CASOS, caminho)
    assert h == hashlib.sha256(caminho.read_bytes()).hexdigest()
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    assert [json.loads(l) for l in linhas] == CASOS


def test_cli_gerar_golden(tmp_path, capsys):
    saida = tmp_path / "golden.jsonl"
    assert main(["gerar-golden", "--n", "8", "--semente", "1", "--saida", str(saida)]) == 0
    texto = capsys.readouterr().out
    assert hashlib.sha256(saida.read_bytes()).hexdigest() in texto
    assert len(saida.read_text(encoding="utf-8").splitlines()) == 8
