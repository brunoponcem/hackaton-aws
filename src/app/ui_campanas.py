"""High-resolution metropolitan campaign map with commune-level aggregates."""

import json
from math import sqrt
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
from ruta.campanas import deployment_proposal, metropolitan_ranking

LABELS = {
    "rank": "Orden",
    "commune": "Comuna",
    "province": "Provincia",
    "people": "Personas pendientes",
    "score": "Puntaje demo",
    "channel": "Canal sugerido",
}
MAP_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
# Fixed count breaks make comparisons stable across clock changes and filters.
COLORS = [
    (5, [56, 189, 248]),
    (10, [45, 212, 191]),
    (15, [250, 204, 21]),
    (20, [251, 146, 60]),
    (25, [244, 63, 94]),
]


def concentration_color(count):
    return next((color for limit, color in reversed(COLORS) if count >= limit), COLORS[0][1])


def campaign_map(rows, *, overview=False, show_heat=True):
    boundaries = json.loads(
        (Path(__file__).parent / "assets/metropolitana-comunas.geojson").read_text(encoding="utf-8")
    )
    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            boundaries,
            id="rm-boundaries",
            filled=False,
            stroked=True,
            get_line_color=[143, 167, 190, 110],
            line_width_min_pixels=1,
        )
    ]
    if rows:
        points = [
            {
                **row,
                "color": concentration_color(row["people"]),
                "radius": sqrt(row["people"]) * 135,
                "label": f"{row['people']}  {row['commune']}",
            }
            for row in rows
        ]
        if show_heat:
            layers.append(
                pdk.Layer(
                    "HeatmapLayer",
                    points,
                    id="rm-heat",
                    get_position="[longitude, latitude]",
                    get_weight="people",
                    radius_pixels=140,
                    intensity=1.1,
                    threshold=0.008,
                    weights_texture_size=2048,
                    color_range=[
                        [22, 78, 99, 0],
                        [8, 145, 178, 100],
                        [45, 212, 191, 170],
                        [250, 204, 21, 210],
                        [251, 146, 60, 235],
                        [244, 63, 94, 250],
                    ],
                )
            )
        layers.extend(
            [
                pdk.Layer(
                    "ScatterplotLayer",
                    points,
                    id="rm-counts",
                    get_position="[longitude, latitude]",
                    get_radius="radius",
                    radius_min_pixels=8,
                    radius_max_pixels=36,
                    get_fill_color="color",
                    get_line_color=[255, 255, 255, 230],
                    stroked=True,
                    line_width_min_pixels=2,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    points,
                    id="rm-labels",
                    get_position="[longitude, latitude]",
                    get_text="label",
                    character_set='"auto"',
                    get_size=15,
                    font_weight=700,
                    get_color=[248, 250, 252],
                    background=True,
                    get_background_color=[15, 23, 42, 235],
                    background_padding=[8, 5],
                    get_pixel_offset=[0, -31],
                    get_text_anchor='"middle"',
                    billboard=True,
                    pickable=True,
                ),
            ]
        )
    return pdk.Deck(
        layers=layers,
        map_style=MAP_STYLE,
        map_provider="mapbox",
        initial_view_state=pdk.ViewState(
            latitude=-33.485 if not overview else -33.55,
            longitude=-70.67 if not overview else -70.78,
            zoom=10.2 if not overview else 8.1,
            min_zoom=7,
            max_zoom=15,
            pitch=0,
            bearing=0,
        ),
        height=650,
        parameters={"clearColor": [0.04, 0.07, 0.12, 1]},
        tooltip={
            "html": "<b>{commune}</b><br/>{people} personas pendientes"
            "<br/>Provincia: {province}<br/>Puntaje demo: {score}"
            "<br/>Ubicación comunal de referencia · simulación",
            "style": {"backgroundColor": "#0f172a", "color": "white", "fontSize": "14px"},
        },
    )


def render_campaigns(state, profiles):
    st.markdown("### Campañas · Región Metropolitana")
    st.caption(
        "PLANIFICACIÓN TERRITORIAL · Casos ficticios agrupados por comuna. "
        "El mapa muestra concentración de pendientes; no domicilios ni densidad de población."
    )
    filters = st.columns([2, 1, 1])
    scope_label = filters[0].selectbox(
        "Población del mapa",
        ["Cola presencial · planificar campañas", "Todo el seguimiento activo · diagnóstico"],
        key="campaign_scope",
    )
    overview = (
        filters[1].selectbox("Encuadre", ["Gran Santiago", "Región completa"]) == "Región completa"
    )
    show_heat = filters[2].toggle("Mostrar calor", value=True)
    scope = "in_person" if scope_label.startswith("Cola") else "active"
    rows = metropolitan_ranking(state, profiles, scope=scope)
    total = sum(row["people"] for row in rows)
    most = rows[0] if rows else None
    metrics = st.columns(3)
    metrics[0].metric("Pendientes visibles en RM", total)
    metrics[1].metric("Comunas con 5+ casos", len(rows))
    metrics[2].metric(
        "Mayor concentración",
        most["commune"] if most else "Sin grupos",
        f"{most['people']} personas" if most else None,
        delta_color="off",
    )
    st.pydeck_chart(
        campaign_map(rows, overview=overview, show_heat=show_heat),
        use_container_width=True,
        height=650,
    )
    st.markdown(
        '<div style="display:flex;gap:22px;flex-wrap:wrap;padding:12px 16px;'
        "border:1px solid #dbe3ed;border-radius:12px;background:#f8fafc;color:#334155;"
        'font-size:14px"><b>Personas por comuna</b>'
        + "".join(
            f'<span><span style="color:rgb{tuple(color)}">●</span> {label}</span>'
            for (_, color), label in zip(
                COLORS, ["5–9", "10–14", "15–19", "20–24", "25+"], strict=True
            )
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Conteos y colores de los círculos usan una escala fija. El halo suaviza la concentración "
        "para orientar la vista; la cifra exacta está en la etiqueta y el ranking. "
        "Se omiten comunas con menos de 5 casos. Cartografía BCN (comunas2017); calles © CARTO / "
        "OpenStreetMap, requieren internet. Se puede ampliar el mapa."
    )
    if not rows:
        st.info(
            "Sin grupos publicables en esta población. Para ver el escenario RM: nueva "
            "simulación → Sin respuestas → Inicializar embudo → Avanzar 19 días. "
            "Los escenarios anteriores se conservan sin reasignar personas."
        )
        return
    left, right = st.columns([3, 2])
    with left:
        st.markdown("#### Dónde concentrar el operativo")
        frame = pd.DataFrame(rows)[list(LABELS)].rename(columns=LABELS)
        st.dataframe(frame, hide_index=True, use_container_width=True)
        st.download_button(
            "Descargar ranking agregado (CSV)",
            frame.to_csv(index=False).encode("utf-8-sig"),
            file_name="ranking-campanas-rm.csv",
            mime="text/csv",
        )
    with right:
        st.markdown("#### Preparar despliegue")
        if scope != "in_person":
            st.info("Vista de diagnóstico. Selecciona Cola presencial para planificar.")
            return
        choices = {row["commune"]: row for row in rows}
        if st.session_state.get("campaign_commune") not in choices:
            st.session_state["campaign_commune"] = next(iter(choices))
        selected = st.selectbox("Comuna para el despliegue", list(choices), key="campaign_commune")
        staff = st.number_input("Personal disponible", min_value=1, max_value=100, value=2)
        capacity = st.number_input(
            "Personas por funcionario al día", min_value=1, max_value=100, value=8
        )
        proposal = deployment_proposal(
            choices[selected], staff=int(staff), daily_capacity=int(capacity)
        )
        st.success(
            f"Propuesta: {selected} · {proposal['people']} personas · "
            f"{proposal['estimated_days']} jornada(s) con {staff} funcionarios."
        )
        st.download_button(
            "Descargar propuesta de despliegue (JSON)",
            json.dumps({"clock": state["clock"]["now"], **proposal}, ensure_ascii=False, indent=2),
            file_name="propuesta-campana-rm.json",
            mime="application/json",
        )
    st.caption(
        "Orden por volumen de pendientes, luego puntaje demo. Puntaje: 1 base + 2 posible "
        "solicitud PGU + 1 antecedente faltante + 1 hito próximo (90 días), según reglas.py. "
        "No es elegibilidad ni agenda/despacho. "
        "Jornadas = personas / capacidad del equipo, hacia arriba."
    )
