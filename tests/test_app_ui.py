import importlib
from pathlib import Path

import pytest


def test_citizen_can_accept_authorize_and_revoke_without_stale_chat(tmp_path, monkeypatch):
    pytest.importorskip("streamlit", reason="Instalar el grupo app para verificar la UI")
    from streamlit.testing.v1 import AppTest

    app_dir = Path(__file__).resolve().parents[1] / "src/app"
    monkeypatch.syspath_prepend(str(app_dir))
    config = importlib.import_module("ruta.config")
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "ui-cases.db")
    monkeypatch.setattr(config, "BEDROCK_MODEL_ID", "")
    app = AppTest.from_file(str(app_dir / "app.py"), default_timeout=20).run()
    assert not app.exception

    def click(label):
        next(button for button in app.button if button.label == label).click().run()
        assert not app.exception

    click("Sí, quiero que me acompañen")
    click("Sí, autorizo")
    click("¿Cuánto recibiría?")
    histories = [
        app.session_state[key]
        for key in app.session_state.filtered_state
        if key.startswith("chat-")
    ]
    assert any(len(history) > 1 for history in histories)
    click("Retirar mi autorización")
    histories = [
        app.session_state[key]
        for key in app.session_state.filtered_state
        if key.startswith("chat-")
    ]
    assert all(len(history) == 1 for history in histories)
    assert all("autorización" in history[0]["texto"] for history in histories)
