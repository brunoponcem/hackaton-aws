"""ChileAtiende portal shell and the MVP help section."""

import base64
import unicodedata
from html import escape
from pathlib import Path
from urllib.parse import quote

import streamlit as st

BASE_URL = "https://www.chileatiende.gob.cl"
LOGO = Path(__file__).resolve().parent / "assets/logo-chileatiende.svg"

CSS = """
<style>
:root {--portal-blue:#0f69b4;--portal-navy:#0d4d82;--portal-red:#eb3c46}
.stApp {background:#fff;color:#272727;font-family:Roboto,Arial,sans-serif}
.block-container {max-width:1280px;padding-top:2rem;padding-bottom:2rem}
[data-testid="stSidebar"] {background:#f7f7f7}
#MainMenu,footer {visibility:hidden}
.portal-header {display:flex;align-items:center;justify-content:space-between;
 border-bottom:1px solid #d9e2eb;padding:0 0 1.3rem;margin-bottom:.6rem;gap:20px}
.portal-logo {width:240px;max-width:48vw;height:65px;object-fit:contain;object-position:left}
.portal-utilities {display:flex;align-items:center;gap:26px;font-size:14px;flex-wrap:wrap}
.portal-utilities a {color:#0d4d82;text-decoration:none;font-weight:500}
.portal-private {background:#0f69b4;color:white!important;padding:11px 18px;border-radius:4px}
.portal-strip {height:4px;background:linear-gradient(to right,#0f69b4 50%,#eb3c46 50%);
 margin-top:14px}
.portal-breadcrumb {font-size:13px;color:#687887;margin:1rem 0}
.portal-breadcrumb a {color:#0f69b4;text-decoration:none}
.portal-hero {background:#edf6fc;border-radius:6px;padding:30px 34px;margin:.5rem 0 1rem;
 border-left:5px solid #0f69b4}
.portal-hero h1 {font-size:36px;color:#0d4d82;line-height:1.2;margin:8px 0 12px;
 letter-spacing:-.6px}
.portal-hero p {font-size:17px;color:#405365;margin:0;max-width:760px;line-height:1.65}
.portal-eyebrow {font-size:12px;font-weight:700;letter-spacing:1px;color:#0f69b4;
 text-transform:uppercase}
.portal-tag {background:#d9edf7;color:#0d4d82;font-size:12px;border-radius:20px;padding:5px 10px}
.portal-section {font-size:25px!important;color:#0d4d82;margin:26px 0 8px!important}
.portal-card {min-height:128px;border:1px solid #dce5ed;border-top:3px solid #0f69b4;
 border-radius:5px;padding:18px 20px;background:white;height:100%}
.portal-card h3 {font-size:18px;color:#0d4d82;margin:0 0 8px}
.portal-card p {font-size:14px;color:#5b6b7a;line-height:1.6;margin:0}
.portal-card small {color:#0f69b4;font-size:12px;font-weight:500}
.portal-help-note {font-size:14px;color:#4a4a4a;line-height:1.6;margin:12px 0 18px}
.portal-footer {visibility:visible;margin-top:45px;border-top:4px solid #0f69b4;padding:25px 5px;
 display:flex;justify-content:space-between;gap:25px;flex-wrap:wrap;color:#4a4a4a;font-size:13px}
.portal-footer a {color:#0d4d82;text-decoration:none}
div[data-testid="stRadio"] > div {gap:1.5rem;border-bottom:1px solid #d9e2eb;padding-bottom:12px}
section[data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"] {
 padding:10px 16px;margin-right:8px;border-bottom:3px solid transparent;color:#0d4d82}
section[data-testid="stMain"] [data-testid="stRadio"]
 label[data-baseweb="radio"] > div:first-child {
 display:none}
section[data-testid="stMain"] [data-testid="stRadio"]
 label[data-baseweb="radio"]:has(input:checked) {
 border-bottom-color:#0f69b4;background:#edf6fc;font-weight:700}
section[data-testid="stMain"] [data-testid="stRadio"] label[data-baseweb="radio"]:focus-within {
 outline:2px solid #0f69b4;outline-offset:2px}
div[data-testid="stChatMessage"] {background:#f3f7fb;border-radius:8px}
@media(max-width:700px){.portal-header{align-items:flex-start}.portal-utilities{gap:12px}
 .portal-hero{padding:22px}.portal-hero h1{font-size:27px}.portal-private{padding:7px 10px}}
</style>
"""

# Labels/URLs verified in the HTML of the official portal on 2026-10-14.
SERVICES = (
    ("Jubilación", "Pensiones, PGU y orientación para tu jubilación.", "/temas/jubilacion"),
    ("Certificados", "Nacimiento, estudios y antecedentes.", "/temas/certificados"),
    (
        "Subsidio Familiar",
        "Consulta la información oficial sobre el SUF.",
        "/fichas/33112-subsidio-familiar-suf",
    ),
    (
        "Pagos por cobrar",
        "Revisa la ficha de pagos por cobrar del IPS.",
        "/fichas/114831-pagos-por-cobrar-del-instituto-de-prevision-social-ips",
    ),
)


def render_header() -> str:
    st.markdown(CSS, unsafe_allow_html=True)
    logo = base64.b64encode(LOGO.read_bytes()).decode("ascii")
    st.markdown(
        f'<header class="portal-header"><a href="{BASE_URL}" target="_blank" '
        f'rel="noopener noreferrer"><img class="portal-logo" alt="ChileAtiende" '
        f'src="data:image/svg+xml;base64,{logo}"></a>'
        '<div class="portal-utilities">'
        f'<a href="{BASE_URL}/ayuda/centro-de-ayuda" target="_blank">Centro de ayuda</a>'
        f'<a href="{BASE_URL}/ayuda" target="_blank">Red de atención</a>'
        '<a class="portal-private" href="https://mi3.chileatiende.gob.cl/micha/inicio" '
        'target="_blank">Mi ChileAtiende ↗</a></div></header>',
        unsafe_allow_html=True,
    )
    return st.radio(
        "Secciones del portal",
        ["Inicio", "Ayuda para tus trámites", "Mi ruta"],
        index=1,
        horizontal=True,
        label_visibility="collapsed",
        key="portal_section",
    )


def hero(section: str) -> None:
    st.markdown(
        f'<div class="portal-breadcrumb"><a href="{BASE_URL}">Inicio</a>'
        f" &nbsp;›&nbsp; {escape(section)}</div>",
        unsafe_allow_html=True,
    )
    title = (
        "Encuentra beneficios y servicios del Estado"
        if section == "Inicio"
        else "Ayuda para todos tus trámites"
    )
    subtitle = (
        "Encuentra información oficial y recibe orientación para dar tu próximo paso."
        if section == "Inicio"
        else "No tienes que hacerlo a solas. Te ayudamos a entender qué necesitas, "
        "ordenar tus pasos y continuar tu trámite, por el canal que prefieras."
    )
    st.markdown(
        '<section class="portal-hero"><span class="portal-eyebrow">ChileAtiende a Tiempo</span>'
        f"<h1>{title}</h1><p>{subtitle}</p></section>",
        unsafe_allow_html=True,
    )
    with st.form("portal_search", border=False):
        query_col, button_col = st.columns([5, 1])
        query = query_col.text_input(
            "¿Qué trámite necesitas?",
            placeholder="Busca un trámite, beneficio o servicio",
            label_visibility="collapsed",
        )
        submitted = button_col.form_submit_button("Buscar", use_container_width=True)
    if submitted and query.strip():
        st.session_state["portal_query"] = query.strip()
    if text := st.session_state.get("portal_query"):
        matches = search_services(text)
        st.caption(f"Resultados para “{text}”")
        for title, _description, path in matches:
            st.link_button(title, BASE_URL + path)
        if not matches:
            st.info("Puedes continuar tu búsqueda en el portal oficial.")
        st.link_button(
            "Ver todos los resultados en ChileAtiende", BASE_URL + "/buscar?query=" + quote(text)
        )


def search_services(query: str) -> list[tuple[str, str, str]]:
    def normalize(value):
        return "".join(
            char
            for char in unicodedata.normalize("NFD", value.lower())
            if not unicodedata.combining(char)
        )

    tokens = normalize(query).split()
    return [
        entry
        for entry in SERVICES
        if all(token in normalize(entry[0] + " " + entry[1]) for token in tokens)
    ]


def render_discovery() -> None:
    st.markdown('<h2 class="portal-section">Destacamos</h2>', unsafe_allow_html=True)
    featured = st.columns(3)
    featured[0].markdown(
        '<article class="portal-card"><small>NUEVO · AYUDA PARA TUS TRÁMITES</small>'
        "<h3>Te acompañamos paso a paso</h3><p>Tu ruta, tus antecedentes y un asistente "
        "para ayudarte a continuar.</p></article>",
        unsafe_allow_html=True,
    )

    def open_help():
        st.session_state["portal_section"] = "Ayuda para tus trámites"

    featured[0].button(
        "Recibir ayuda para mi trámite", on_click=open_help, use_container_width=True
    )
    featured[1].markdown(
        '<article class="portal-card"><small>INFORMACIÓN PERSONAL</small>'
        "<h3>Mi ChileAtiende</h3><p>Continúa en tu sesión privada del portal oficial.</p>"
        "</article>",
        unsafe_allow_html=True,
    )
    featured[1].link_button(
        "Ir a Mi ChileAtiende ↗",
        "https://mi3.chileatiende.gob.cl/micha/inicio",
        use_container_width=True,
    )
    featured[2].markdown(
        '<article class="portal-card"><small>MOMENTO DE VIDA</small>'
        "<h3>Prepara tu jubilación</h3><p>Encuentra orientación oficial para este momento "
        "de tu vida.</p></article>",
        unsafe_allow_html=True,
    )
    featured[2].link_button(
        "Revisar jubilación ↗", BASE_URL + "/temas/jubilacion", use_container_width=True
    )
    st.markdown('<h2 class="portal-section">Lo más buscado</h2>', unsafe_allow_html=True)
    for col, (title, description, path) in zip(st.columns(4), SERVICES, strict=True):
        with col:
            st.markdown(
                f'<article class="portal-card"><h3>{title}</h3><p>{description}</p></article>',
                unsafe_allow_html=True,
            )
            st.link_button("Consultar información ↗", BASE_URL + path, use_container_width=True)
    st.markdown('<h2 class="portal-section">Momentos de vida</h2>', unsafe_allow_html=True)
    moments = (
        (
            "Iniciar jubilación",
            "Organiza tu pensión y prepara tu solicitud de PGU.",
            "/hito-vida/Iniciar+jubilación",
        ),
        (
            "Acceder a una vivienda",
            "Encuentra la orientación oficial para este momento.",
            "/hito-vida/Acceder+a+una+vivienda",
        ),
        (
            "Quedar sin trabajo",
            "Consulta tus alternativas en el portal oficial.",
            "/momentos-de-vida",
        ),
    )
    for col, (title, description, path) in zip(st.columns(3), moments, strict=True):
        with col:
            st.markdown(
                f'<article class="portal-card"><h3>{title}</h3><p>{description}</p></article>',
                unsafe_allow_html=True,
            )
            st.link_button("Ver orientación ↗", BASE_URL + path, use_container_width=True)
    st.markdown(
        '<h2 class="portal-section">Servicios del Estado por temas</h2>', unsafe_allow_html=True
    )
    for col, (title, description, path) in zip(st.columns(3), SERVICES[:3], strict=True):
        with col:
            st.markdown(
                f'<article class="portal-card"><h3>{title}</h3><p>{description}</p></article>',
                unsafe_allow_html=True,
            )
            st.link_button("Explorar este tema ↗", BASE_URL + path, use_container_width=True)
    st.link_button("Conoce todos los servicios por temas", BASE_URL + "/temas")


def render_help_intro() -> None:
    st.markdown(
        '<h2 class="portal-section">Un próximo paso claro, en un solo lugar</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="portal-help-note">Cuéntanos qué necesitas, prepara tus antecedentes y '
        "retoma donde quedaste. El asistente de ayuda te acompaña durante el recorrido.</p>",
        unsafe_allow_html=True,
    )
    for col, title, description in zip(
        st.columns(3),
        ["1. Entiende tu situación", "2. Prepara tu trámite", "3. Continúa acompañado"],
        [
            "Revisamos contigo qué sabes y qué falta, con tu autorización.",
            "Encuentra documentos, pasos y fechas en tu ruta personalizada.",
            "Pregunta al asistente o continúa con un ejecutivo sin empezar de nuevo.",
        ],
        strict=True,
    ):
        col.markdown(
            f'<article class="portal-card"><h3>{title}</h3><p>{description}</p></article>',
            unsafe_allow_html=True,
        )
    st.caption(
        "Prototipo del hackatón · La ruta personalizada de este MVP cubre jubilación y PGU. "
        "Los demás trámites se consultan en el portal oficial. Datos de demostración sintéticos."
    )
    st.markdown(
        '<h2 class="portal-section">Tu acompañamiento: jubilación y PGU</h2>',
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<footer class="portal-footer"><div><b>ChileAtiende a Tiempo</b><br>'
        "Prototipo de ayuda para trámites · Hackatón AWS 2026</div>"
        f'<div><b>Servicios del Estado</b><br><a href="{BASE_URL}/temas">Explorar por temas</a>'
        f'<br><a href="{BASE_URL}/instituciones">Instituciones</a></div>'
        f'<div><b>¿Necesitas ayuda?</b><br><a href="{BASE_URL}/ayuda/atencion-telefonica">'
        "Call Center 101</a><br>"
        f'<a href="{BASE_URL}/sucursalvirtual">Videoatención</a></div></footer>',
        unsafe_allow_html=True,
    )
