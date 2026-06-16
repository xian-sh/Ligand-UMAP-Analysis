from __future__ import annotations

from .config import parse_args
from .pipeline import run_pipeline


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    run_pipeline(cfg)


if __name__ == "__main__":
    main()

