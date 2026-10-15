import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_cli_runs_without_streamlit_and_exports_persistent_state(tmp_path):
    script = ROOT / "scripts/colador_backend.py"
    db, contacts, output = tmp_path / "cases.db", tmp_path / "contacts.csv", tmp_path / "out.json"
    command = [sys.executable, str(script), "--db", str(db), "--output", str(output)]
    initialized = subprocess.run(
        [*command, "init", "--contacts", str(contacts), "--simulate"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    assert json.loads(initialized.stdout)["totals"]["detected"] > 0
    assert contacts.exists()
    subprocess.run(
        [*command, "advance", "--days", "19", "--simulate"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["clock"]["now"] == "2026-10-27T09:00:00"
    assert exported["totals"]["started"] > 0
    assert exported["totals"]["in_person"] > 0


def test_visual_funnel_advances_and_declining_stops_further_contact(tmp_path, monkeypatch):
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    app_dir = ROOT / "src/app"
    monkeypatch.syspath_prepend(str(app_dir))
    monkeypatch.setenv("FUNNEL_DEMO_DB", str(tmp_path / "demo.db"))
    app = AppTest.from_file(str(app_dir / "demo_embudo.py"), default_timeout=30).run()
    assert not app.exception
    app.radio[0].set_value("Sin respuestas")

    def click(label):
        next(button for button in app.button if button.label == label).click().run()
        assert not app.exception

    click("Inicializar embudo")
    assert len(app.metric) == 5
    selected = app.selectbox[0].value
    click("Abrir / contestar")
    click("Avanzar 7 días")
    click("Declinar")
    assert next(metric for metric in app.metric if metric.label == "Declinaron").value == "1"
    click("Avanzar 19 días")
    from src.app.ruta.colador import Funnel

    state = Funnel(tmp_path / "demo.db").snapshot()
    person = next(person for person in state["people"] if person["run"] == selected)
    assert person["status"] == "declined" and person["alert_level"] == 0
    assert not person["next_at"]
