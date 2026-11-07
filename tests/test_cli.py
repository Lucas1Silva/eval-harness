import pytest

from harness.cli import main


def test_help_responde_e_sai_com_zero(capsys):
    with pytest.raises(SystemExit) as saida:
        main(["--help"])
    assert saida.value.code == 0
    assert "harness" in capsys.readouterr().out


def test_sem_argumentos_retorna_zero():
    assert main([]) == 0
