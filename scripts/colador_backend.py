"""Run the demo funnel without Streamlit, Bedrock, emails or external calls."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from src.app.ruta import config
from src.app.ruta.colador import Funnel
from src.app.ruta.contacto import generate_contacts, load_contacts, save_contacts
from src.app.ruta.datos import cargar_perfiles

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=config.DB_PATH)
    parser.add_argument("--output", type=Path, help="Exportar snapshot JSON completo")
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init")
    initialize.add_argument("--seed", type=int, default=20261008)
    initialize.add_argument("--date", type=date.fromisoformat, default=config.FECHA_REFERENCIA)
    initialize.add_argument("--contacts", type=Path, default=ROOT / "data/synthetic/contacto.csv")
    initialize.add_argument("--simulate", action="store_true")
    advance = commands.add_parser("advance")
    advance.add_argument("--days", type=int, required=True)
    advance.add_argument("--simulate", action="store_true")
    response = commands.add_parser("respond")
    response.add_argument("--run", required=True)
    response.add_argument(
        "--response", choices=["opened", "answered", "started", "declined"], required=True
    )
    commands.add_parser("status")
    args = parser.parse_args(argv)
    if args.output and args.output.resolve() == args.db.resolve():
        parser.error("El snapshot JSON no puede sobrescribir la base SQLite.")
    funnel = Funnel(args.db)
    try:
        if args.command == "init":
            profiles = cargar_perfiles()
            if args.contacts.exists():
                contacts = load_contacts(args.contacts)
            else:
                contacts = generate_contacts(profiles, args.seed)
                save_contacts(args.contacts, contacts)
            state = funnel.initialize(
                profiles, contacts, reference_date=args.date, seed=args.seed, simulate=args.simulate
            )
        elif args.command == "advance":
            state = funnel.advance(args.days, simulate=args.simulate)
        elif args.command == "respond":
            state = funnel.respond(args.run, args.response)
        else:
            state = funnel.snapshot()
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {key: state[key] for key in ("clock", "totals", "funnel", "source")},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
