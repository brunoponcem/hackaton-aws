"""Verify/install Johann's opt-in Kiro context without changing shared setup."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

ROLE_DIR = Path(__file__).resolve().parent
ROOT = ROLE_DIR.parents[1]


def templates() -> dict[str, str]:
    context = (ROLE_DIR / "contexto-codear-johann.md").read_text(encoding="utf-8")
    if not context.startswith("---\ninclusion: manual\n"):
        raise ValueError("La guía debe tener inclusión manual.")
    if len(context.split()) > 1800 or "#[[file:" in context:
        raise ValueError("Contexto excesivo o referencias que importan documentos completos.")
    ignore = (ROLE_DIR / "kiroignore-johann.template").read_text(encoding="utf-8")
    return {".kiro/steering/johann-context.md": context, ".kiroignore": ignore}


def install(root: Path, contents: dict[str, str]) -> None:
    # Validate every target before writing anything; never replace a user's config.
    targets = {root / path: text for path, text in contents.items()}
    for target, content in targets.items():
        if not target.resolve().is_relative_to(root.resolve()):
            raise ValueError("Destino fuera del checkout.")
        if target.exists() and target.read_text(encoding="utf-8") != content:
            raise ValueError(f"Configuración existente diferente: {target}. Revisar manualmente.")
    for target, content in targets.items():
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)


def verify(contents: dict[str, str]) -> None:
    with TemporaryDirectory(prefix="johann-kiro-") as temporary:
        root = Path(temporary)
        install(root, contents)
        install(root, contents)  # Identical installation is idempotent.
        for relative, expected in contents.items():
            if (root / relative).read_text(encoding="utf-8") != expected:
                raise ValueError("La instalación no conserva el contenido.")
        target = root / ".kiroignore"
        target.write_text("configuración propia\n", encoding="utf-8")
        try:
            install(root, contents)
        except ValueError:
            if target.read_text(encoding="utf-8") != "configuración propia\n":
                raise ValueError("Se alteró la configuración existente.") from None
        else:
            raise ValueError("La instalación debe rechazar sobrescrituras.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--install", action="store_true")
    args = parser.parse_args()
    contents = templates()
    verify(contents)
    if args.install:
        install(ROOT, contents)
        print("Contexto local preparado. En Kiro: #johann-context + tarea concreta.")
    else:
        print("OK: contexto manual, acotado, instalación idempotente y sin sobrescrituras.")


if __name__ == "__main__":
    main()
