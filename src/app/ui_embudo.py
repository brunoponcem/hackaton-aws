"""Visual test harness for the same persistent backend used by the CLI."""

import json

import pandas as pd
import streamlit as st
from ruta.colador import ACTIVE, STAGES, Funnel
from ruta.contacto import generate_contacts
from ui_campanas import render_campaigns

STATUS_LABELS = {"active": "En seguimiento", "started": "Trámite iniciado", "declined": "Declinó"}
EVENT_LABELS = {
    "signal": "Nueva alerta agregada al caso",
    "entered": "Entró a la etapa",
    "skipped": "Canal no disponible: se salta",
    "attempt": "Intento simulado",
    "queued": "Pendiente de campaña presencial",
    "started": "Inició trámite",
    "declined": "Declinó: se detiene",
    "opened": "Abrió correo (sin inicio)",
    "answered": "Contestó (sin inicio)",
}


def render_funnel(profiles, db_path=None):
    engine = Funnel(db_path)
    state = engine.snapshot()
    st.markdown("## Embudo de contacto")
    st.info(
        "SIMULACIÓN · No se envían correos, no se realizan llamadas ni visitas. "
        "Contactos, respuestas y plazos son datos de demostración."
    )
    st.caption(
        "Fuente: contacto-y-campanas.md · Email → llamada → trabajo → presencial. "
        "Solo sale del embudo quien inicia su trámite o declina; abrir/contestar no basta."
    )
    controls = st.columns([2, 1])
    mode = controls[0].radio(
        "Comportamiento de las respuestas",
        ["Respuestas simuladas", "Sin respuestas"],
        horizontal=True,
    )
    seed = controls[1].number_input(
        "Semilla de la campaña", value=20261008, min_value=0, disabled=state["clock"] is not None
    )
    simulate = mode == "Respuestas simuladas"
    if not state["clock"]:
        st.caption(
            "La detección reutiliza reglas.py sobre 500 perfiles. "
            "Escenario territorial: comunas de la Región Metropolitana, asignadas sintéticamente."
        )
        if st.button("Inicializar embudo", type="primary"):
            engine.initialize(
                profiles,
                generate_contacts(profiles, int(seed), territory="metropolitana"),
                seed=int(seed),
                simulate=simulate,
            )
            st.rerun()
        return

    st.success(
        f"Reloj simulado: {state['clock']['now'].replace('T', ' ')} · "
        f"Semilla {state['clock']['seed']}"
    )
    for col, days in zip(st.columns(4), [1, 5, 7, 19], strict=True):
        if col.button(f"Avanzar {days} {'día' if days == 1 else 'días'}", use_container_width=True):
            engine.advance(days, simulate=simulate)
            st.rerun()
    st.caption(
        "Política demo: email 7 días; llamadas en días 0, 2 y 5; trabajo 7 días. "
        "Presencial queda en cola para planificar una campaña."
    )

    totals = state["totals"]
    metrics = ("Detectadas", "Iniciaron trámite", "Declinaron", "En seguimiento", "En presencial")
    keys = ("detected", "started", "declined", "active", "in_person")
    for col, label, key in zip(st.columns(5), metrics, keys, strict=True):
        col.metric(label, totals[key])

    st.markdown("### Del contacto general al acompañamiento presencial")
    import altair as alt

    data = pd.DataFrame(state["funnel"])
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X(
                "reached:Q", title="Personas que llegaron a cada etapa (incluye canales saltados)"
            ),
            y=alt.Y("label:N", sort=list(STAGES.values()), title=None),
            color=alt.Color(
                "label:N",
                legend=None,
                scale=alt.Scale(
                    domain=list(STAGES.values()), range=["#0f69b4", "#408fc9", "#78b2d9", "#eb9847"]
                ),
            ),
            tooltip=[
                alt.Tooltip("label:N", title="Etapa"),
                alt.Tooltip("reached:Q", title="Llegaron"),
                alt.Tooltip("attempts:Q", title="Intentos simulados"),
                alt.Tooltip("active:Q", title="Siguen en esta etapa"),
            ],
        )
    )
    st.altair_chart(chart.properties(height=240), use_container_width=True)
    st.dataframe(
        data.rename(
            columns={
                "label": "Etapa",
                "reached": "Llegaron",
                "attempts": "Intentos simulados",
                "active": "Pendientes actuales",
            }
        ).drop(columns="stage"),
        hide_index=True,
        use_container_width=True,
    )

    render_campaigns(state, profiles)

    st.markdown("### Personas y próximo contacto")
    rows = [
        {
            "RUN": person["run"],
            "Nombre": person["name"],
            "Edad": person["age"],
            "Etapa": person["stage_label"],
            "Estado": STATUS_LABELS[person["status"]],
            "Provincia simulada": person["contact"]["province"],
            "Próximo contacto": person["next_at"] or "—",
        }
        for person in state["people"]
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=260)

    if not state["people"]:
        return
    selected = st.selectbox("Inspeccionar persona", [person["run"] for person in state["people"]])
    person = next(person for person in state["people"] if person["run"] == selected)
    st.caption(f"{person['name']} · {person['stage_label']} · {STATUS_LABELS[person['status']]}")
    actions = st.columns(3)
    responses = ("opened" if person["stage"] == 1 else "answered", "started", "declined")
    for col, label, response in zip(
        actions, ["Abrir / contestar", "Inició su trámite", "Declinar"], responses, strict=True
    ):
        if col.button(label, disabled=person["status"] != ACTIVE, use_container_width=True):
            engine.respond(selected, response)
            st.rerun()

    history = [
        {
            "Fecha simulada": event["at"],
            "Etapa": STAGES[event["stage"]],
            "Evento": EVENT_LABELS[event["kind"]],
            "Detalle": event["detail"].get("reason") or event["detail"].get("message", ""),
        }
        for event in state["events"]
        if event["run"] == selected
    ]
    st.dataframe(pd.DataFrame(history), hide_index=True, use_container_width=True)
    with st.expander("Ver snapshot del backend"):
        st.json(
            {"clock": state["clock"], "totals": totals, "funnel": state["funnel"], "person": person}
        )
    st.download_button(
        "Descargar estado completo (JSON sintético)",
        data=json.dumps(state, ensure_ascii=False, indent=2),
        file_name="embudo-simulado.json",
        mime="application/json",
    )
