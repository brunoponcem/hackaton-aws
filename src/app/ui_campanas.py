"""High-resolution metropolitan campaign map with commune-level aggregates."""

import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
from ruta.campanas import metropolitan_locations, metropolitan_ranking
from ruta.despliegue import propose_campaign_area

LABELS = {
    "rank": "Orden",
    "commune": "Comuna",
    "province": "Provincia",
    "people": "Personas pendientes",
    "score": "Puntaje demo",
    "channel": "Canal sugerido",
}
MAP_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"


def campaign_map(
    rows,
    locations=(),
    *,
    overview=False,
    show_heat=True,
    show_points=False,
    show_totals=False,
    detail="Barrios",
    campaign_area=None,
):
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
    if locations:
        homes = [
            {**point, "tooltip_title": point["commune"], "tooltip_detail": point["address"]}
            for point in locations
        ]
        if show_heat:
            layers.append(
                pdk.Layer(
                    "HeatmapLayer",
                    homes,
                    id="rm-heat",
                    get_position="[longitude, latitude]",
                    get_weight="weight",
                    radius_pixels=55 if detail == "Barrios" else 90,
                    intensity=1.8,
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
        if show_points or not show_heat:
            layers.append(
                pdk.Layer(
                    "ScatterplotLayer",
                    homes,
                    id="rm-simulated-homes",
                    get_position="[longitude, latitude]",
                    get_radius=35,
                    radius_min_pixels=3,
                    radius_max_pixels=7,
                    get_fill_color=[125, 225, 250, 220],
                    get_line_color=[230, 250, 255, 200],
                    stroked=True,
                    line_width_min_pixels=0.5,
                    pickable=True,
                )
            )
    if campaign_area:
        props = campaign_area["properties"]
        area_feature = {
            **campaign_area,
            "properties": {
                **props,
                "tooltip_title": "Área propuesta de campaña",
                "tooltip_detail": f"{props['people']} personas · radio "
                f"{props['radius_m'] / 1000:g} km · "
                f"{props['estimated_days']} jornada(s)",
            },
        }
        layers.extend(
            [
                pdk.Layer(
                    "GeoJsonLayer",
                    area_feature,
                    id="rm-campaign-area",
                    filled=True,
                    stroked=True,
                    get_fill_color=[250, 204, 21, 26],
                    get_line_color=[250, 204, 21, 245],
                    line_width_min_pixels=3,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    [
                        {
                            "longitude": props["center_longitude"],
                            "latitude": props["center_latitude"],
                            "label": f"ÁREA PROPUESTA · {props['people']} personas",
                            "tooltip_title": "Área propuesta de campaña",
                            "tooltip_detail": f"Radio {props['radius_m'] / 1000:g} km · "
                            f"{props['coverage_percent']}% de casos del mapa",
                        }
                    ],
                    id="rm-campaign-label",
                    get_position="[longitude, latitude]",
                    get_text="label",
                    character_set='"auto"',
                    get_size=14,
                    font_weight=700,
                    get_color=[250, 204, 21],
                    background=True,
                    get_background_color=[15, 23, 42, 245],
                    background_padding=[10, 6],
                    get_pixel_offset=[0, 35],
                    pickable=True,
                ),
            ]
        )
    if rows and show_totals:
        points = [
            {
                **row,
                "label": f"{row['people']}  {row['commune']}",
                "tooltip_title": row["commune"],
                "tooltip_detail": f"{row['people']} personas pendientes · total comunal",
            }
            for row in rows
        ]
        layers.extend(
            [
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
            "html": "<b>{tooltip_title}</b><br/>{tooltip_detail}"
            "<br/>SIMULACIÓN · No es un domicilio RSH",
            "style": {"backgroundColor": "#0f172a", "color": "white", "fontSize": "14px"},
        },
    )


def render_campaigns(state, profiles):
    st.markdown("### Campañas · Región Metropolitana")
    st.caption(
        "PLANIFICACIÓN TERRITORIAL · Calor calculado desde ubicaciones individuales ficticias "
        "dentro de la RM. Direcciones simuladas, sin conexión con domicilios del RSH."
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
    display = st.columns([1, 1, 1])
    show_points = display[0].checkbox("Ver ubicaciones simuladas", value=False)
    show_totals = display[1].checkbox("Totales por comuna", value=True)
    detail = display[2].selectbox("Detalle territorial", ["Barrios", "Sectores amplios"])
    scope = "in_person" if scope_label.startswith("Cola") else "active"
    rows = metropolitan_ranking(state, profiles, scope=scope)
    locations = metropolitan_locations(state, rows, scope=scope)
    area = None
    with st.expander("Área de despliegue propuesta según el heatmap", expanded=True):
        if scope != "in_person":
            st.info(
                "Para proponer un despliegue, selecciona Cola presencial. "
                "Esta vista es diagnóstica."
            )
            show_area = False
        else:
            settings = st.columns([2, 1, 1])
            radius = settings[0].slider(
                "Radio de cobertura (metros)", min_value=500, max_value=3000, value=1500, step=250
            )
            staff = settings[1].number_input(
                "Personal disponible", min_value=1, max_value=100, value=2
            )
            capacity = settings[2].number_input(
                "Personas por funcionario al día", min_value=1, max_value=100, value=8
            )
            show_area = st.checkbox("Mostrar área propuesta en el mapa", value=True)
            area = propose_campaign_area(
                locations, radius_m=radius, staff=int(staff), daily_capacity=int(capacity)
            )
            if area:
                info = area["properties"]
                st.success(
                    f"Propuesta: cubrir {info['people']} personas en un radio de "
                    f"{radius / 1000:g} km · {info['coverage_percent']}% de los casos del mapa "
                    f"· {info['estimated_days']} jornada(s) estimada(s)."
                )
                st.caption(
                    "El contorno amarillo prioriza la mayor cantidad de casos cercanos "
                    "dentro del radio elegido. La capacidad del equipo estima las jornadas."
                )
            else:
                st.info(
                    "No hay un área con al menos cinco casos dentro de este radio. "
                    "Amplía el radio o avanza la simulación."
                )
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
        campaign_map(
            rows,
            locations,
            overview=overview,
            show_heat=show_heat,
            show_points=show_points,
            show_totals=show_totals,
            detail=detail,
            campaign_area=area if show_area else None,
        ),
        use_container_width=True,
        height=650,
    )
    st.markdown(
        '<div style="display:flex;gap:22px;flex-wrap:wrap;padding:12px 16px;'
        "border:1px solid #dbe3ed;border-radius:12px;background:#f8fafc;color:#334155;"
        'font-size:14px"><b>Concentración local</b><span>Baja</span>'
        '<span style="display:inline-block;width:240px;height:12px;border-radius:8px;'
        'background:linear-gradient(90deg,#38bdf8,#2dd4bf,#facc15,#fb923c,#f43f5e)"></span>'
        "<span>Alta</span><span>Más ubicaciones cercanas → mayor intensidad</span>" + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Cada ubicación ficticia suma una persona al calor: ya no se coloca el total en el centro "
        "de la comuna. La intensidad es relativa al encuadre y al suavizado; el ranking conserva "
        "los conteos exactos. Solo comunas con 5+ casos. Cartografía BCN (comunas2017); © CARTO / "
        "OpenStreetMap, requieren internet. Se puede ampliar el mapa."
    )
    if rows and len(locations) != total:
        st.warning(
            f"{len(locations)} de {total} casos visibles tienen una ubicación sintética válida; "
            "los demás no se dibujan ni se concentran en un centroide."
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
        st.markdown("#### Área de campaña recomendada")
        if scope != "in_person":
            st.info("Vista de diagnóstico. Selecciona Cola presencial para planificar.")
            return
        if not area:
            st.caption("Ajusta el radio arriba para encontrar un sector con cinco o más casos.")
            return
        info = area["properties"]
        st.write(" · ".join(f"{commune}: {count}" for commune, count in info["communes"].items()))
        st.write(
            f"**{info['people']} personas** · {info['area_km2']} km² aproximados · "
            f"{info['estimated_days']} jornada(s)."
        )
        st.caption(
            "Propuesta geométrica de cobertura, no un lugar habilitado para atender. "
            "Puede cruzar límites comunales. El responsable valida acceso, sede y recorridos."
        )
        st.download_button(
            "Descargar propuesta de despliegue (JSON)",
            json.dumps({"clock": state["clock"]["now"], **info}, ensure_ascii=False, indent=2),
            file_name="propuesta-campana-rm.json",
            mime="application/json",
        )
        st.download_button(
            "Descargar área propuesta (GeoJSON)",
            json.dumps(area, ensure_ascii=False, indent=2),
            file_name="area-campana-rm.geojson",
            mime="application/geo+json",
        )
    st.caption(
        "Orden por volumen de pendientes, luego puntaje demo. Puntaje: 1 base + 2 posible "
        "solicitud PGU + 1 antecedente faltante + 1 hito próximo (90 días), según reglas.py. "
        "No es elegibilidad ni agenda/despacho. "
        "Jornadas = personas / capacidad del equipo, hacia arriba."
    )
