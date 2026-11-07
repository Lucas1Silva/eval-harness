import argparse
from pathlib import Path

from harness import golden


def _gerar_golden(args: argparse.Namespace) -> int:
    casos = golden.gerar_golden(args.n, args.semente)
    hash_arquivo = golden.gravar_jsonl(casos, Path(args.saida))
    print(f"{len(casos)} casos gravados em {args.saida}")
    print(f"sha256 {hash_arquivo}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="harness",
        description="Harness de avaliação de um LLM que extrai dados de cadastros de fornecedores.",
    )
    sub = parser.add_subparsers(dest="comando")

    p = sub.add_parser("gerar-golden", help="gera o golden set sintético")
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--semente", type=int, default=42)
    p.add_argument("--saida", default="data/golden_v1.jsonl")
    p.set_defaults(func=_gerar_golden)

    args = parser.parse_args(argv)
    if args.comando is None:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
