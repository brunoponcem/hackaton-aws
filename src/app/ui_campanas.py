"""Executive-facing simulated campaign map, ranking and workload proposal."""

import json
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pydeck as pdk
import streamlit as st
from ruta.campanas import campaign_ranking, deployment_proposal

LABELS = {
    "rank": "Prioridad",
    "region": "Región",
    "province": "Provincia",
    "people": "Personas pendientes",
    "score": "Puntaje demo",
    "channel": "Canal sugerido",
}


def campaign_map(rows):
    """Local outline and aggregate markers; no API key, tiles or personal coordinates."""
    outline = json.loads(
        (Path(__file__).parent / "assets/campaign-basemap.geojson").read_text(encoding="utf-8")
    )
    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            outline,
            filled=True,
            stroked=True,
            get_fill_color=[226, 235, 242],
            get_line_color=[137, 160, 180],
            line_width_min_pixels=1,
        )
    ]
    if rows:
        maximum = max(row["people"] for row in rows)
        points = [
            {**row, "color": [230, int(175 - 125 * row["people"] / maximum), 35, 190]}
            for row in rows
        ]
        layers.extend(
            [
                pdk.Layer(
                    "HeatmapLayer",
                    points,
                    get_position="[longitude, latitude]",
                    get_weight="people",
                    radius_pixels=55,
                    intensity=1,
                    threshold=0.05,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    points,
                    get_position="[longitude, latitude]",
                    get_radius="people * 2500",
                    radius_min_pixels=9,
                    radius_max_pixels=35,
                    get_fill_color="color",
                    get_line_color=[120, 40, 15],
                    stroked=True,
                    line_width_min_pixels=1,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    points,
                    get_position="[longitude, latitude]",
                    get_text="province",
                    get_color=[25, 45, 65],
                    get_size=13,
                    get_pixel_offset=[18, 0],
                    get_text_anchor='"start"',
                ),
            ]
        )
    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=-31, longitude=-71.5, zoom=3.2),
        map_provider="mapbox",
        # Streamlit 1.40 ignores style dictionaries in its frontend. A local data
        # URL keeps the empty basemap intact instead of falling back to remote tiles.
        map_style="data:application/json," + quote('{"version":8,"sources":{},"layers":[]}'),
        tooltip={
            "html": "<b>{province}</b><br/>{people} personas pendientes"
            "<br/>Puntaje demo: {score}<br/>Ubicación representativa, no domicilio"
        },
    )


def render_campaigns(state, profiles):
    st.markdown("### Campañas territoriales · vista de ejecutivos")
    st.caption(
        "SIMULACIÓN · Seis provincias ilustrativas, con ubicaciones asignadas; no son datos "
        "territoriales del RSH. El color y el tamaño representan personas pendientes, "
        "no tasas de población. Puntos aproximados de ciudades de referencia, no domicilios."
    )
    scope_label = st.selectbox(
        "Población del mapa",
        ["Cola presencial · planificar campañas", "Todo el seguimiento activo · diagnóstico"],
        key="campaign_scope",
    )
    scope = "in_person" if scope_label.startswith("Cola") else "active"
    ranking = campaign_ranking(state, profiles, scope=scope)
    regions = ["Todas las regiones", *sorted({row["region"] for row in ranking})]
    # A clock change can remove a province/region that fell below the threshold.
    if st.session_state.get("campaign_region") not in regions:
        st.session_state["campaign_region"] = regions[0]
    region = st.selectbox("Región de campaña", regions, key="campaign_region")
    rows = [row for row in ranking if region == regions[0] or row["region"] == region]
    st.pydeck_chart(campaign_map(rows), use_container_width=True)
    st.caption(
        "Mayor intensidad = más personas. Solo se publican provincias con 5 o más casos "
        "en la población seleccionada; no se muestran grupos pequeños ni sus ubicaciones. "
        "Base cartográfica: Natural Earth, dominio público. Arrastra y usa zoom para explorar."
    )
    if not rows:
        st.info(
            "No hay provincias publicables en esta vista. Para probar: nueva simulación → "
            "Sin respuestas → Inicializar embudo → Avanzar 19 días."
        )
        return
    st.dataframe(
        pd.DataFrame(rows)[list(LABELS)].rename(columns=LABELS),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "Ranking por suma de puntos demo: 1 por persona + 2 si podría solicitar PGU "
        "+ 1 si falta un antecedente PGU + 1 si tiene un hito en los próximos 90 días. "
        "Fuente: reglas.py y contacto-y-campanas.md. No es una decisión de elegibilidad."
    )
    st.download_button(
        "Descargar ranking agregado (CSV)",
        pd.DataFrame(rows)[list(LABELS)]
        .rename(columns=LABELS)
        .to_csv(index=False)
        .encode("utf-8-sig"),
        file_name="ranking-campanas-sintetico.csv",
        mime="text/csv",
    )
    if scope != "in_person":
        st.info("Vista de diagnóstico. Selecciona Cola presencial para preparar un despliegue.")
        return
    choices = {f"{row['province']} · {row['region']}": row for row in rows}
    if st.session_state.get("campaign_province") not in choices:
        st.session_state["campaign_province"] = next(iter(choices))
    selected = st.selectbox("Provincia para el despliegue", list(choices), key="campaign_province")
    left, right = st.columns(2)
    staff = left.number_input("Personal disponible", min_value=1, max_value=100, value=2)
    capacity = right.number_input(
        "Personas por funcionario al día", min_value=1, max_value=100, value=8
    )
    proposal = deployment_proposal(
        choices[selected], staff=int(staff), daily_capacity=int(capacity)
    )
    st.success(
        f"Propuesta: {proposal['province']} · {proposal['people']} personas · "
        f"{proposal['staff']} funcionarios · {proposal['estimated_days']} jornada(s) estimada(s)."
    )
    st.caption(
        "Estimación = personas / capacidad diaria del equipo, redondeada hacia arriba. "
        "El responsable define lugar, agenda y cobertura. No reserva horas ni despacha visitas."
    )
    st.download_button(
        "Descargar propuesta de despliegue (JSON)",
        json.dumps({"clock": state["clock"]["now"], **proposal}, ensure_ascii=False, indent=2),
        file_name="propuesta-campana-simulada.json",
        mime="application/json",
    )
