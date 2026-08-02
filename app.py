import time
from io import BytesIO

import streamlit_authenticator as stauth
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit_authenticator as stauth

from auth import (
    feedback_completado_hoy,
    get_conciliaciones_hoy,
    get_users_for_auth,
    guardar_feedback,
    registrar_historial,
    registrar_nuevo_usuario_db,
    get_user_state,
    update_user_state,
)
import datetime
from logic import procesar_conciliacion, generar_excel_coloreado

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Concilia · Conciliación Bancaria Inteligente",
    page_icon="LOGO SIN FONDO .png.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DESIGN TOKENS ─────────────────────────────────────────────
COLOR_BOTON_DESCARGA = "#19a28d"
COLOR_BARRAS_ENCUESTA = "#19a28d"
COLOR_SELECTORES = "#19a28d"

PRIMARY   = "#06b6d4"  # Turquesa / Cian Vibrante
PRIMARY2  = "#082032"  # Azul Oscuro / Petróleo
SUCCESS   = "#38bdf8"  # Celeste / Azul Cielo
WARNING   = "#f59e0b"  # Amber
DANGER    = "#c12727"  # Rose
BG        = "#090d16"  # Deep Rich Blue-Black
BG2       = "#0f172a"  # Dark Slate Blue
CARD      = "#1e293b"  # Slate Blue Card
BORDER    = "#0e7490"  # Borde Cian / Turquesa
TEXT      = "#FFFFFF"  # Off White
MUTED     = "#94a3b8"  # Slate Gray
COL_PREVIEW = "#19a28d"
DF_BG     = "#082032"
DF_TEXT   = "#ffffff"

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ─ Fonts y Estética General ──────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif !important;
}}

/* ─ Fondo de la Aplicación ───────────────────────────────── */
.stApp {{
    background: radial-gradient(circle at 50% 50%, {BG2} 0%, {BG} 100%) !important;
    color: {TEXT};
}}

/* ─ Ocultar Menús de Streamlit ───────────────────────────── */
#MainMenu, footer {{ visibility: hidden; }}
header {{ background-color: transparent !important; }}

/* ─ Ajustes del Logo (Sin borde, transparente y centrado) ── */
[data-testid="stImage"] {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 0 auto !important;
}}
[data-testid="stImage"] img {{
    object-fit: contain !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
}}

.logo-center {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}}

.logo-center img {{
    margin: 0 auto !important;
}}

/* ─ Contenedor Login Premium ─────────────────────────────── */
.login-card {{
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(126, 187, 137, 0.3);
    border-radius: 24px;
    padding: 30px 40px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 50px rgba(126, 187, 137, 0.05);
    margin-top: 10px;
}}

.login-header {{
    text-align: center;
    margin-bottom: 25px;
}}

.login-title {{
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, {PRIMARY} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}}

.login-subtitle {{
    font-size: 0.95rem;
    color: {MUTED};
}}

/* ─ Inputs y Formularios ─────────────────────────────────── */
div[data-baseweb="input"] {{
    background-color: {PRIMARY2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    transition: all 0.25s ease !important;
    overflow: hidden !important;
}}
div[data-baseweb="select"] > div {{
    border-color: {COLOR_SELECTORES} !important;
}}
div[data-baseweb="input"] > div {{
    background-color: transparent !important;
}}
div[data-baseweb="input"]:focus-within {{
    border-color: {PRIMARY} !important;
    box-shadow: 0 0 10px rgba(126, 187, 137, 0.25) !important;
}}
input, textarea {{
    color: {TEXT} !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}}
input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear,
input::-webkit-credentials-auto-fill-button {{
    display: none !important;
}}

/* ─ Botón General / Login ────────────────────────────────── */
/* Fix definitivo para hacer visibles TODOS los botones y sus textos (incluido el Login) */
.stButton > button, 
[data-testid="stForm"] button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #4a8254 100%) !important;
    border: none !important;
    border-radius: 8px !important;
}}
[data-testid="stDownloadButton"] button {{
    background: {COLOR_BOTON_DESCARGA} !important;
}}

.stButton > button[kind="primary"]:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(126, 187, 137, 0.5) !important;
}}

/* ─ Botón Exclusivo de Cerrar Sesión (Sidebar) ───────────── */
div[data-testid="stSidebar"] .stButton > button {{
    background: rgba(193, 39, 39, 0.15) !important;
    border: 1px solid rgba(193, 39, 39, 0.4) !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
    font-weight: 600 !important;
    margin-top: 10px;
}}
div[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(193, 39, 39, 0.35) !important;
    border-color: {DANGER} !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}}

/* ─ File Uploader Drag & Drop ─────────── */
[data-testid="stFileUploaderDropzone"] {{
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(126, 187, 137, 0.4) !important;
    border-radius: 16px !important;
    padding: 25px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: {PRIMARY} !important;
    background: rgba(126, 187, 137, 0.08) !important;
    box-shadow: 0 4px 20px rgba(126, 187, 137, 0.15) !important;
}}

[data-testid="stFileUploaderDropzone"] button {{
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}
[data-testid="stFileUploaderDropzone"] span {{
    color: {TEXT} !important;
}}

/* ─ Sidebar Custom ───────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: {BG} !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}}

/* ─ Slider & Progress bar ──────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
    background: {PRIMARY} !important;
    border-color: {PRIMARY} !important;
}}
[data-testid="stSlider"] div[class*="Track"] div:first-child,
[data-testid="stProgressBar"] > div > div {{
    background: {COLOR_BARRAS_ENCUESTA} !important;
    border-radius: 99px !important;
}}
[data-testid="stProgressBar"] > div {{
    background: rgba(255,255,255,0.1) !important;
    border-radius: 99px !important;
}}

/* ─ COMPONENTES PROPIOS DE LA LÓGICA DE LA APP ORIGINAL ──── */
/* ─ Tabs ───────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {CARD};
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important;
    color: {MUTED} !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {PRIMARY} 0%, #4a8254 100%) !important;
    color: #ffffff !important;
}}

/* ─ Dataframe & Expander ───────────────────────────────── */
[data-testid="stDataFrame"], [data-testid="stExpander"] {{
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    background: {CARD} !important;
    overflow: hidden !important;
}}

/* ─ Divider & Alerts ───────────────────────────────────── */
hr {{ border-color: rgba(255,255,255,0.1) !important; margin: 1.5rem 0 !important; }}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}

/* ─ Clases Custom (Métricas, Sidebar, Encuesta) ────────── */
.sidebar-divider {{
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 12px 0;
}}
.sidebar-label {{
    font-size: 11px; font-weight: 600; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 4px;
}}
.sidebar-value {{
    font-size: 14px; font-weight: 500; color: {TEXT};
}}
.page-title {{
    font-size: 1.8rem; font-weight: 700; color: {TEXT};
    line-height: 1.2; margin-bottom: 4px;
}}
.page-subtitle {{
    font-size: 0.9rem; color: {MUTED}; margin-bottom: 1.5rem;
}}
.section-label {{
    font-size: 0.85rem; font-weight: 600; color: {TEXT};
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;
}}
.metric-card {{
    background: {CARD}; border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 18px 20px; text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}}
.metric-val {{
    font-size: 2.2rem; font-weight: 700; line-height: 1; margin-bottom: 4px;
}}
.metric-lbl {{
    font-size: 0.75rem; font-weight: 600; color: {MUTED};
    text-transform: uppercase; letter-spacing: 0.07em;
}}
.survey-wrap {{
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid {PRIMARY};
    border-radius: 16px; padding: 32px 36px; margin: 24px 0;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}}
.survey-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(6, 182, 212, 0.1); border: 1px solid {PRIMARY};
    border-radius: 20px; padding: 5px 14px;
    font-size: 0.82rem; color: {PRIMARY}; font-weight: 600;
    margin-bottom: 14px;
}}
.survey-title {{
    font-size: 1.25rem; font-weight: 600; color: {TEXT}; margin-bottom: 2px;
}}
.survey-sub {{
    font-size: 0.88rem; color: {MUTED}; margin-bottom: 24px;
}}
.limit-card {{
    background: rgba(245, 158, 11, 0.1); border: 1px solid {WARNING};
    border-radius: 14px; padding: 28px; text-align: center; margin: 20px 0;
}}
.progress-label {{
    font-size: 0.88rem; color: {MUTED}; margin-bottom: 6px;
}}
label p, .st-form label p {{
    color: {TEXT} !important;
    font-weight: 600 !important;
}}
input::placeholder {{
    color: rgba(255,255,255,0.4) !important;
}}

/* Custom para Streamlit Authenticator Form */
div[data-testid="stForm"] {{
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(126, 187, 137, 0.3);
    border-radius: 24px;
    padding: 30px 40px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 50px rgba(126, 187, 137, 0.05);
    margin-top: 10px;
}}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────

RATING_LABELS = ["", "Muy mala", "Mala", "Regular", "Por debajo del promedio",
                 "Promedio", "Buena", "Muy buena", "Excelente", "Sobresaliente", "Perfecta"]

def rating_display(val: int) -> str:
    return f"Puntuacion: {val}/10 — {RATING_LABELS[val]}"

def get_index(cols, keywords):
    for i, c in enumerate(cols):
        if any(k in str(c).lower() for k in keywords):
            return i
    return 0

def plotly_light_layout(title: str, height: int = 300) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=13), x=0),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        legend=dict(font=dict(color=MUTED), bgcolor=CARD),
        margin=dict(t=44, b=16, l=16, r=16),
        height=height,
    )

# ── AUTH SETUP ────────────────────────────────────────────────
credentials = get_users_for_auth()
if credentials is None:
    st.error("No se pudo conectar a la base de datos.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials,
    "concilia_session_v3",
    "signature_key_secreta",
    cookie_expiry_days=30,
)

# ── LOGIN & REGISTRO ──────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    _l, center, _r = st.columns([1, 1.4, 1])
    with center:
        st.markdown('<div class="logo-center" style="margin-top: 20px; margin-bottom: -15px;">', unsafe_allow_html=True)
        st.image("LOGO SIN FONDO .png.png", width=250)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 25px;">
            <div class="login-title">¡Bienvenido!</div>
            <div class="login-subtitle">Iniciá sesión o registrate para acceder al sistema</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_registro = st.tabs(["Iniciar Sesion", "Crear Cuenta"])

        with tab_login:
            try:
                authenticator.login()
            except Exception as e:
                st.error(f"Error en autenticacion: {e}")

            if st.session_state.get("authentication_status") is False:
                st.error("Usuario o contrasena incorrectos. Volve a intentarlo.")

        with tab_registro:
            with st.form("registro_form"):
                st.subheader("Nueva Cuenta")
                new_user = st.text_input("Username", placeholder="ej: santi").strip().lower()
                new_name = st.text_input("Nombre Completo", placeholder="ej: Santino Domeniconi").strip()
                new_email = st.text_input("Email (@gmail.com)", placeholder="ej: santi@gmail.com").strip().lower()
                new_pwd = st.text_input("Contrasena", type="password", placeholder="Escribi tu contrasena").strip()
                submit_reg = st.form_submit_button("Registrarse")

                if submit_reg:
                    if not new_user or not new_name or not new_email or not new_pwd:
                        st.error("Todos los campos son obligatorios.")
                    elif not new_email.endswith("@gmail.com"):
                        st.error("El correo electronico debe ser @gmail.com.")
                    else:
                        success, msg = registrar_nuevo_usuario_db(new_user, new_name, new_pwd, new_email)
                        if success:
                            st.success(msg + " Ya podes iniciar sesion en la otra pestana.")
                        else:
                            st.error(msg)

    st.stop()

# ── MAIN APP (autenticado) ────────────────────────────────────
username: str = st.session_state["username"]
name: str     = st.session_state["name"]

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-center" style="padding-top: 20px; flex-direction: column;">', unsafe_allow_html=True)
    st.image("LOGO SIN FONDO .png.png", width=250)
    st.markdown(f"""
        <h2 style="margin-top: 10px; color: {TEXT}; font-weight: 800; font-size: 1.5rem; text-align: center;">CONCILIA</h2>
        <div style="color: {MUTED}; font-size: 0.85rem; text-align: center;">Conciliacion Bancaria Automatizada</div>
    </div>
    <div style="border-top: 1px solid rgba(255, 255, 255, 0.05); margin: 15px 0;"></div>
    """, unsafe_allow_html=True)

    # User info
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(6, 182, 212, 0.4); border-radius: 12px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 0.75rem; text-transform: uppercase; color: {MUTED}; font-weight: 700; letter-spacing: 0.05em;">Usuario Activo</span>
        <div style="font-size: 1.1rem; font-weight: 600; color: {TEXT}; margin-top: 2px;">{name}</div>
        <div style="font-size: 0.8rem; color: {SUCCESS}; font-weight: 500; margin-top: 4px; display: flex; align-items: center; gap: 4px;">
            <span style="height: 8px; width: 8px; background-color: {SUCCESS}; border-radius: 50%; display: inline-block;"></span> @{username}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Daily usage and lock logic
    realizadas, max_conc, bloqueo_hasta, encuesta_hab = get_user_state(username)
    
    if username == "admin":
        max_conc = 99999
        display_max = "∞"
    else:
        display_max = str(max_conc)

    st.markdown(f"""
    <div class="sidebar-label" style="margin-top:4px;">Uso de hoy</div>
    <div class="sidebar-value" style="margin-bottom:8px;">{realizadas} de {display_max} conciliaciones</div>
    """, unsafe_allow_html=True)
    
    pct = 0.0 if username == "admin" else (realizadas / max_conc if max_conc > 0 else 1.0)
    st.progress(pct)

    if realizadas == 1 and max_conc == 1 and not encuesta_hab:
        st.markdown(f"""
        <div style="background:{PRIMARY}10;border:1px solid {PRIMARY}30;border-radius:8px;
                    padding:10px 12px;margin-top:10px;font-size:12px;color:{PRIMARY};font-weight:500;">
            Completá la encuesta post-conciliacion y desbloqueá una conciliacion extra hoy
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="sidebar-divider" style="margin-top:14px;"></div>', unsafe_allow_html=True)
    authenticator.logout("Cerrar sesion")

# ── HEADER ────────────────────────────────────────────────────
st.markdown('<div class="logo-center" style="margin-top: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
try:
    st.image("Concilia titulo.png", use_container_width=True)
except Exception:
    st.markdown("""
    <div class="page-title">Conciliacion Bancaria</div>
    <div class="page-subtitle">Detectá automaticamente coincidencias entre tu extracto bancario y tu registro contable</div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VISTA RESULTADOS
# ══════════════════════════════════════════════════════════════
if "r_coin" in st.session_state:
    coincidencias = st.session_state["r_coin"]
    coincidencias_bajas = st.session_state.get("r_bajas", pd.DataFrame())
    solo_banco    = st.session_state["r_banco"]
    solo_contable = st.session_state["r_conta"]
    col_b         = st.session_state.get("r_col_b", "")
    col_c         = st.session_state.get("r_col_c", "")

    total  = len(coincidencias) + len(coincidencias_bajas) + len(solo_banco) + len(solo_contable)
    pct_ok = ((len(coincidencias) + len(coincidencias_bajas)) / total * 100) if total else 0.0

    if st.session_state.get("show_survey"):
        st.markdown(f"""
        <div style="background:{PRIMARY}10;border:1px solid {PRIMARY}30;border-radius:10px;
                    padding:10px 16px;margin-bottom:16px;font-size:13px;color:{PRIMARY};
                    display:flex;align-items:center;gap:8px;font-weight:500;">
            <span>Tu encuesta está al pie de esta página — completala y desbloqueás una conciliacion extra hoy</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Metricas ──────────────────────────────────────────
    st.markdown('<div class="page-title" style="font-size:1.3rem;">Resultados</div>', unsafe_allow_html=True)
    st.write("")

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    for _col, val, label, color in [
        (m1, len(coincidencias), "Coincidencias", PRIMARY),
        (m2, len(solo_banco),    "Solo Banco",    WARNING),
        (m3, len(solo_contable), "Solo Contable", DANGER),
        (m4, f"{pct_ok:.1f}%",   "Tasa match",   SUCCESS),
    ]:
        with _col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color:{color};">{val}</div>
                <div class="metric-lbl">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # ── Graficos ──────────────────────────────────────────
    ch1, ch2 = st.columns(2, gap="medium")

    with ch1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Coincidencias", "Solo Banco", "Solo Contable"],
            values=[len(coincidencias), len(solo_banco), len(solo_contable)],
            hole=0.62,
            marker=dict(colors=[PRIMARY, WARNING, DANGER], line=dict(color=CARD, width=2)),
            textinfo="label+percent",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="%{label}: %{value} registros<extra></extra>",
        )])
        fig_pie.update_layout(**plotly_light_layout("Distribucion de registros"))
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        try:
            def _sum(df, col):
                if df.empty or col not in df.columns:
                    return 0.0
                return pd.to_numeric(df[col], errors="coerce").abs().sum()

            fig_bar = go.Figure(data=[go.Bar(
                x=["Coincidencias", "Solo Banco", "Solo Contable"],
                y=[_sum(coincidencias, f"{col_b}_banco"), _sum(solo_banco, col_b), _sum(solo_contable, col_c)],
                marker_color=[PRIMARY, WARNING, DANGER],
                text=[f"${v:,.0f}" for v in [_sum(coincidencias, f"{col_b}_banco"), _sum(solo_banco, col_b), _sum(solo_contable, col_c)]],
                textposition="outside",
                textfont=dict(color=TEXT, size=11),
                hovertemplate="%{x}: $%{y:,.2f}<extra></extra>",
            )])
            layout = plotly_light_layout("Montos por categoria")
            layout.update(dict(
                xaxis=dict(showgrid=False, tickfont=dict(color=MUTED)),
                yaxis=dict(showgrid=True, gridcolor=BORDER, tickfont=dict(color=MUTED), zeroline=False),
                showlegend=False,
            ))
            fig_bar.update_layout(**layout)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            st.info("Grafico de montos no disponible para estas columnas.")

    st.divider()

    # ── Tabs de datos ─────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        f"Coincidencias ({len(coincidencias)})",
        f"Baja Similitud ({len(coincidencias_bajas)})",
        f"Solo Banco ({len(solo_banco)})",
        f"Solo Contable ({len(solo_contable)})",
    ])
    with tab1:
        if coincidencias.empty:
            st.info("No se encontraron coincidencias entre los archivos.")
        else:
            st.dataframe(coincidencias, use_container_width=True, height=420)
    with tab2:
        if coincidencias_bajas.empty:
            st.info("No hay registros de baja similitud.")
        else:
            st.dataframe(coincidencias_bajas, use_container_width=True, height=420)
    with tab3:
        if solo_banco.empty:
            st.success("Todos los registros del banco tienen coincidencia contable.")
        else:
            st.dataframe(solo_banco, use_container_width=True, height=420)
    with tab4:
        if solo_contable.empty:
            st.success("Todos los registros contables tienen coincidencia bancaria.")
        else:
            st.dataframe(solo_contable, use_container_width=True, height=420)

    # ── Descarga ──────────────────────────────────────────
    st.divider()
    use_colored_export = st.session_state.get("use_colored_export", False)
    
    if use_colored_export:
        banco_original = st.session_state.get("banco_original")
        contable_original = st.session_state.get("contable_original")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            if banco_original is not None:
                out_banco = generar_excel_coloreado(banco_original)
                st.download_button(
                    label="Descargar Extracto Bancario Valido",
                    data=out_banco.getvalue(),
                    file_name="Extracto_Bancario_Validado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )
        with col_d2:
            if contable_original is not None:
                out_conta = generar_excel_coloreado(contable_original)
                st.download_button(
                    label="Descargar Registro Contable Valido",
                    data=out_conta.getvalue(),
                    file_name="Registro_Contable_Validado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            (coincidencias if not coincidencias.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
                writer, index=False, sheet_name="Coincidencias")
            (coincidencias_bajas if not coincidencias_bajas.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
                writer, index=False, sheet_name="Baja Similitud")
            (solo_banco if not solo_banco.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
                writer, index=False, sheet_name="Solo Banco")
            (solo_contable if not solo_contable.empty else pd.DataFrame({"Mensaje": ["Sin datos"]})).to_excel(
                writer, index=False, sheet_name="Solo Contable")
        st.download_button(
            label="Descargar Reporte Excel",
            data=output.getvalue(),
            file_name="reporte_conciliacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )

    st.divider()

    # ── Encuesta ──────────────────────────────────────────
    if st.session_state.get("show_survey"):
        st.markdown(f"""
        <div class="survey-wrap">
            <div class="survey-badge">Completá la encuesta · Desbloqueás +1 conciliacion hoy</div>
            <div class="survey-title">¿Cómo fue tu experiencia?</div>
            <div class="survey-sub">Tu feedback nos ayuda a mejorar Concilia. Tardás menos de 30 segundos.</div>
        </div>
        """, unsafe_allow_html=True)

        r_ui = st.slider("Interfaz y experiencia de uso", 1, 10, 7, key="s_ui",
                         help="¿Qué tan fácil e intuitiva te resultó la interfaz?")
        st.caption(rating_display(r_ui))
        st.write("")

        r_res = st.slider("Precision y utilidad de los resultados", 1, 10, 7, key="s_res",
                          help="¿Los resultados reflejan correctamente tu conciliacion?")
        st.caption(rating_display(r_res))
        st.write("")

        comentario = st.text_area(
            "Comentarios adicionales (opcional)",
            placeholder="¿Qué mejorarías? ¿Qué te resultó más útil? ¿Encontraste algún problema?",
            key="s_comment",
        )

        btn1, btn2 = st.columns([4, 1])
        with btn1:
            if st.button("Enviar y desbloquear conciliacion extra", type="primary",
                         use_container_width=True, key="btn_enviar"):
                guardar_feedback(username, r_ui, r_res, comentario)
                st.session_state["show_survey"] = False
                
                update_user_state(username, realizadas, 2, bloqueo_hasta, True)
                
                st.rerun()
        with btn2:
            if st.button("Saltar", use_container_width=True, key="btn_saltar"):
                st.session_state["show_survey"] = False
                st.rerun()

    # ── Accion post-encuesta ──────────────────────────────
    else:
        if realizadas < max_conc:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;
                        padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
                <div>
                    <div style="font-size:14px;font-weight:600;color:{TEXT};margin-bottom:2px;">
                        ¿Querés conciliar otro archivo?
                    </div>
                    <div style="font-size:12px;color:{MUTED};">
                        Tenés {'ilimitadas' if username == 'admin' else (max_conc - realizadas)} conciliacion{'es' if (username == 'admin' or max_conc - realizadas > 1) else ''} disponible{'s' if (username == 'admin' or max_conc - realizadas > 1) else ''} hoy
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Nueva Conciliacion", type="primary", use_container_width=True, key="btn_nueva"):
                for k in ["r_coin", "r_bajas", "r_banco", "r_conta", "r_col_b", "r_col_c", "show_survey", "use_colored_export", "banco_original", "contable_original"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            st.markdown(f"""
            <div class="limit-card">
                <div style="font-size:1rem;font-weight:600;color:#92400e;margin-bottom:4px;">Limite diario alcanzado</div>
                <div style="font-size:0.85rem;color:#b45309;">Usaste tus {max_conc} conciliaciones de hoy. Volvé en 24 horas.</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VISTA UPLOAD
# ══════════════════════════════════════════════════════════════
else:
    realizadas, max_conc, bloqueo_hasta, encuesta_hab = get_user_state(username)
    if username == "admin":
        max_conc = 99999

    if realizadas >= max_conc:
        st.markdown(f"""
        <div class="limit-card">
            <div style="font-size:1.1rem;font-weight:600;color:#92400e;margin-bottom:6px;">
                Limite diario alcanzado
            </div>
            <div style="font-size:0.88rem;color:#b45309;">
                Usaste tus {max_conc} conciliaciones de hoy. Volvé en 24 horas para continuar.
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── Carga de archivos ─────────────────────────────
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="section-label">Extracto Bancario</div>', unsafe_allow_html=True)
            file_banco = st.file_uploader(
                "Extracto bancario", type=["csv", "xlsx"],
                label_visibility="collapsed", key="file_banco", accept_multiple_files=False
            )
        with col2:
            st.markdown('<div class="section-label">Registro Contable</div>', unsafe_allow_html=True)
            file_contable = st.file_uploader(
                "Registro contable", type=["csv", "xlsx"],
                label_visibility="collapsed", key="file_contable", accept_multiple_files=False
            )

        if file_banco is None or file_contable is None:
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.4); border: 1px dashed rgba(6, 182, 212, 0.5); border-radius: 12px; padding: 20px; text-align: center; margin-top: 30px;">
                <h4 style="margin: 0 0 4px 0; font-size: 1.05rem; color: #ffffff;">Esperando archivos...</h4>
                <p style="margin: 0; color: {MUTED}; font-size: 0.9rem;">
                    Arrastrá y soltá ambos archivos Excel o CSV para continuar.
                </p>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.divider()
            st.markdown('<div class="section-label">Ajuste de Encabezados (Opcional)</div>', unsafe_allow_html=True)
            row_col1, row_col2 = st.columns(2, gap="large")
            with row_col1:
                skip_b_str = st.text_input("Fila de encabezados - Extracto Bancario", value="1", key="skip_b", help="Escribe el número de la fila. (Ej: 1, 2, 3...)")
                try: skip_banco = int(skip_b_str)
                except: skip_banco = 1
            with row_col2:
                skip_c_str = st.text_input("Fila de encabezados - Registro Contable", value="1", key="skip_c", help="Escribe el número de la fila. (Ej: 1, 2, 3...)")
                try: skip_contable = int(skip_c_str)
                except: skip_contable = 1
                
            use_split_monto = st.checkbox("Dividir Montos en Débitos y Créditos", help="Usa esta opción si tus archivos tienen los montos divididos en dos columnas separadas (Débito y Crédito) en lugar de una sola.")

            # ── Lectura de archivos ───────────────────────
            try:
                df_banco_raw = pd.read_csv(file_banco, header=None) if file_banco.name.endswith(".csv") else pd.read_excel(file_banco, header=None)
                df_contable_raw = pd.read_csv(file_contable, header=None) if file_contable.name.endswith(".csv") else pd.read_excel(file_contable, header=None)
                
                def procesar_encabezados(df_raw, fila_encabezado):
                    idx = fila_encabezado - 1
                    if idx >= len(df_raw):
                        return pd.DataFrame()
                    df_work = df_raw.iloc[idx:].copy()
                    df_work.columns = df_work.iloc[0]
                    df_work = df_work[1:]
                    df_work = df_work.dropna(how='all')
                    df_work.columns = [str(c) if pd.notna(c) else f"Unnamed_{i}" for i, c in enumerate(df_work.columns)]
                    return df_work

                df_banco = procesar_encabezados(df_banco_raw, skip_banco)
                df_contable = procesar_encabezados(df_contable_raw, skip_contable)

            except Exception as e:
                st.error(f"No se pudo leer uno de los archivos: {e}")
                st.stop()

            # ── Mapeo de columnas ─────────────────────────
            st.divider()
            st.markdown('<div class="section-label">Mapeo de Columnas</div>', unsafe_allow_html=True)
            st.caption("Verificá que cada selector apunta a la columna correcta de tu archivo")

            map1, map2 = st.columns(2, gap="large")
            with map1:
                st.markdown(f"<div style='font-size:13px;font-weight:600;color:{TEXT};margin-bottom:8px;'>Extracto Bancario</div>", unsafe_allow_html=True)
                banco_cols      = ["Ninguno"] + df_banco.columns.tolist()
                
                if use_split_monto:
                    col_deb_b  = st.selectbox("Monto Débito", banco_cols[1:], key="deb_b")
                    col_cred_b = st.selectbox("Monto Crédito", banco_cols[1:], key="cred_b")
                    col_monto_banco = None
                else:
                    col_monto_banco = st.selectbox("Monto",       banco_cols[1:], index=get_index(banco_cols[1:], ["importe","monto","valor","suma","total"]),        key="monto_b")
                    col_deb_b, col_cred_b = None, None
                    
                col_fecha_banco = st.selectbox("Fecha",       banco_cols, index=get_index(banco_cols, ["fecha","date","dia"]),                       key="fecha_b")
                col_desc_banco  = st.selectbox("Descripcion", banco_cols, index=get_index(banco_cols, ["descripcion","detalle","concepto"]), key="desc_b")
            with map2:
                st.markdown(f"<div style='font-size:13px;font-weight:600;color:{TEXT};margin-bottom:8px;'>Registro Contable</div>", unsafe_allow_html=True)
                conta_cols      = ["Ninguno"] + df_contable.columns.tolist()
                
                if use_split_monto:
                    col_deb_c  = st.selectbox("Monto Débito", conta_cols[1:], key="deb_c")
                    col_cred_c = st.selectbox("Monto Crédito", conta_cols[1:], key="cred_c")
                    col_monto_conta = None
                else:
                    col_monto_conta = st.selectbox("Monto",       conta_cols[1:], index=get_index(conta_cols[1:], ["importe","monto","valor","suma","total"]),        key="monto_l")
                    col_deb_c, col_cred_c = None, None
                    
                col_fecha_conta = st.selectbox("Fecha",       conta_cols, index=get_index(conta_cols, ["fecha","date","dia"]),                       key="fecha_l")
                col_desc_conta  = st.selectbox("Descripcion", conta_cols, index=get_index(conta_cols, ["descripcion","detalle","concepto"]), key="desc_l")

            with st.expander("Vista previa de los archivos cargados"):
                vp1, vp2 = st.columns(2)
                with vp1:
                    st.caption("Extracto Bancario — primeras filas")
                    st.dataframe(df_banco.head(), use_container_width=True)
                with vp2:
                    st.caption("Registro Contable — primeras filas")
                    st.dataframe(df_contable.head(), use_container_width=True)

            st.divider()
            st.markdown('<div class="section-label">Opciones de Exportación</div>', unsafe_allow_html=True)
            use_colored_export = st.checkbox("Exportar archivos originales coloreados", value=False, help="Descarga los archivos originales pintando las filas según su estado (Verde: Coincidencia, Azul: Baja similitud, Rojo: Sin coincidencia)")
            st.divider()

            # ── Boton procesar ────────────────────────────
            if st.button("Procesar Conciliacion", type="primary", use_container_width=True, disabled=(realizadas >= max_conc)):
                prog_bar  = st.progress(0)
                prog_text = st.empty()

                def step(pct: int, msg: str):
                    prog_bar.progress(pct)
                    prog_text.markdown(f'<div class="progress-label">{msg}</div>', unsafe_allow_html=True)

                step(10, "Limpiando y normalizando datos...")
                time.sleep(0.35)
                step(35, "Buscando coincidencias exactas por monto...")
                time.sleep(0.2)
                
                col_f_b = col_fecha_banco if col_fecha_banco != "Ninguno" else None
                col_f_c = col_fecha_conta if col_fecha_conta != "Ninguno" else None
                col_d_b = col_desc_banco if col_desc_banco != "Ninguno" else None
                col_d_c = col_desc_conta if col_desc_conta != "Ninguno" else None

                if use_split_monto:
                    df_banco['_Monto_Temp'] = (
                        pd.to_numeric(df_banco[col_deb_b].astype(str).str.replace(',', '.'), errors='coerce').abs().fillna(0) -
                        pd.to_numeric(df_banco[col_cred_b].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                    )
                    df_contable['_Monto_Temp'] = (
                        pd.to_numeric(df_contable[col_cred_c].astype(str).str.replace(',', '.'), errors='coerce').fillna(0) -
                        pd.to_numeric(df_contable[col_deb_c].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                    )
                    # Pre-parsear fechas del contable si vienen como string (formato DD/MM/YY con espacios)
                    if col_f_c and df_contable[col_f_c].dtype == object:
                        df_contable[col_f_c] = pd.to_datetime(
                            df_contable[col_f_c].astype(str).str.strip(),
                            dayfirst=True, errors='coerce'
                        )
                    col_m_b_final = '_Monto_Temp'
                    col_m_c_final = '_Monto_Temp'
                    st.session_state["r_col_b"] = col_deb_b
                    st.session_state["r_col_c"] = col_deb_c
                else:
                    col_m_b_final = col_monto_banco
                    col_m_c_final = col_monto_conta
                    st.session_state["r_col_b"] = col_monto_banco
                    st.session_state["r_col_c"] = col_monto_conta

                coincidencias_altas, coincidencias_bajas, solo_banco, solo_contable, banco_work_res, contable_work_res = procesar_conciliacion(
                    df_banco, df_contable,
                    col_f_b, col_m_b_final, col_d_b,
                    col_f_c, col_m_c_final, col_d_c,
                    tolerancia_dias=4 if use_split_monto else 3
                )
                
                # Restaurar a los archivos Raw preservando encabezados basuras
                df_banco_raw['Estado_Color'] = None
                df_banco_raw['Similitud_%'] = None
                df_banco_raw.update(banco_work_res[['Estado_Color', 'Similitud_%']])
                
                df_contable_raw['Estado_Color'] = None
                df_contable_raw['Similitud_%'] = None
                df_contable_raw.update(contable_work_res[['Estado_Color', 'Similitud_%']])

                step(72, "Aplicando algoritmo de fuzzy matching...")
                time.sleep(0.3)
                step(90, "Calculando estadisticas y generando reporte...")
                time.sleep(0.25)
                step(100, "Conciliacion completada exitosamente.")
                time.sleep(0.55)

                prog_bar.empty()
                prog_text.empty()

                registrar_historial(username, len(coincidencias_altas) + len(coincidencias_bajas), len(solo_banco), len(solo_contable))
                
                # Actualizar estado del usuario y calcular bloqueo 24h
                new_realizadas = realizadas + 1
                new_bloqueo = datetime.datetime.now() + datetime.timedelta(days=1) if new_realizadas >= max_conc else bloqueo_hasta
                update_user_state(username, new_realizadas, max_conc, new_bloqueo, encuesta_hab)

                st.session_state["r_coin"]       = coincidencias_altas
                st.session_state["r_bajas"]      = coincidencias_bajas
                st.session_state["r_banco"]      = solo_banco
                st.session_state["r_conta"]      = solo_contable
                # r_col_b y r_col_c ya se guardaron arriba en la logica
                st.session_state["show_survey"]  = not encuesta_hab
                st.session_state["use_colored_export"] = use_colored_export
                st.session_state["banco_original"] = df_banco_raw
                st.session_state["contable_original"] = df_contable_raw

                st.rerun()