"""Independent local visual test: uv run --group app streamlit run src/app/demo_embudo.py."""

import os
from pathlib import Path
from uuid import uuid4

import streamlit as st
from ruta.datos import cargar_perfiles
from ui_embudo import render_funnel

st.set_page_config(page_title="Demo · Embudo ChileAtiende", page_icon="📊", layout="wide")
st.markdown("# ChileAtiende a Tiempo · Backend del embudo")
st.caption("Demo local independiente: usa funnel-demo.db, separada de los casos de la página.")
default_path = Path(os.getenv("FUNNEL_DEMO_DB", Path(__file__).resolve().parent / "funnel-demo.db"))
if st.button("Nueva simulación (conservar la anterior)"):
    st.session_state["funnel_demo_path"] = str(
        default_path.with_name(f"funnel-demo-{uuid4().hex[:8]}.db")
    )
    st.rerun()
render_funnel(cargar_perfiles(), st.session_state.get("funnel_demo_path", default_path))
