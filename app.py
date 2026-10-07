"""
Agente de Revisión Diaria y Semanal — app de una sola página en Streamlit.

Ejecutar:   pip install streamlit
            streamlit run app.py
Colores consistentes: crea .streamlit/config.toml con  [theme]  base = "light"
Los cierres diarios se guardan en registro.json (junto a app.py).
"""
import json
from datetime import date, timedelta
from html import escape
from pathlib import Path

import streamlit as st

ARCHIVO = Path(__file__).with_name("registro.json")

# ───────────────────────── Datos ─────────────────────────
def cargar_registros():
    try:
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def guardar_registro(reg):
    """Un cierre por día: si ya existe el de hoy, se reemplaza."""
    datos = [r for r in cargar_registros() if r["fecha"] != reg["fecha"]] + [reg]
    ARCHIVO.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def registros_ultimos_7_dias():
    desde = (date.today() - timedelta(days=6)).isoformat()
    return [r for r in cargar_registros() if r["fecha"] >= desde]


# Informe de ejemplo: define la estructura exacta que debe devolver el LLM.
INFORME_DEMO = {
    "logros": [
        "Rotación de Ginecología sin faltas y 2 casos presentados en el pase de sala.",
        "5 de 7 bloques de repaso espaciado completados.",
        "Cierre nocturno registrado 6 de 7 días: la racha sube de nivel.",
    ],
    "desafios": [
        "3 repasos orales postergados por cansancio después de guardia.",
        "Tiempo perdido en el celular justo antes del bloque de estudio.",
        "Poca práctica con preguntas tipo examen integrador.",
    ],
    "mejoras": [
        {"titulo": "Blindar el bloque de estudio", "detalle": "2 h fijas a las 16:00, con el celular fuera de la habitación."},
        {"titulo": "Repaso oral con un compañero", "detalle": "Dos sesiones de 30 min por semana, explicando en voz alta."},
        {"titulo": "Simulacro semanal", "detalle": "El sábado, 20 preguntas tipo integrador y revisión de cada error."},
    ],
    "plan": {
        "enfoque": "Consolidar Ginecología y Obstetricia con práctica activa.",
        "meta": "Completar 3 simulacros del examen integrador.",
        "habito": "15 min de repaso espaciado antes de salir al hospital.",
    },
}


def _dia(r):
    return f'{r["fecha"][8:10]}/{r["fecha"][5:7]}'


def generar_informe_semanal(registros):
    """
    ╔══════════════════════════════════════════════════════════════╗
    ║  🔌 AQUÍ SE CONECTA EL LLM (informe de los domingos)         ║
    ╚══════════════════════════════════════════════════════════════╝
    1. Arma el prompt con los `registros` de los últimos 7 días.
    2. Pide que analice cada día por separado y luego sintetice la semana.
    3. Exige respuesta SOLO en JSON con las claves de INFORME_DEMO y devuélvela.

    Ejemplo (pip install anthropic; define ANTHROPIC_API_KEY en el entorno):

        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1500,
            system=("Eres mi Agente de Revisión semanal (Life RPG, 6.º año de medicina). "
                    "Analiza primero cada día y luego la semana. Responde SOLO con JSON: "
                    "{logros, desafios, mejoras:[{titulo, detalle}], plan:{enfoque, meta, habito}}"),
            messages=[{"role": "user", "content": json.dumps(registros, ensure_ascii=False)}],
        )
        return json.loads(msg.content[0].text)   # si viene dentro de ``` límpialo antes
    """
    # Mientras no haya LLM: victorias y desafíos salen de tus registros reales;
    # mejoras y plan siguen siendo de ejemplo.
    informe = dict(INFORME_DEMO)
    if registros:
        informe["logros"] = [f'{_dia(r)}: {r["bien"]}' for r in registros if r["bien"]] or informe["logros"]
        informe["desafios"] = [f'{_dia(r)}: {r["mal"]}' for r in registros if r["mal"]] or informe["desafios"]
    return informe


# ───────────────────────── Estilos ─────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Instrument+Sans:wght@400;500;700&display=swap');
:root{--fondo:#E8EEF0;--tinta:#0E2A35;--verde:#1F7A5C;--alerta:#C4443A;--xp:#F2B705;--linea:#C9D5DA;--suave:#53707B}
.stApp{background:var(--fondo);color:var(--tinta)}
.stApp,.stApp p,.stApp label,.stApp textarea,.stApp button{font-family:'Instrument Sans',system-ui,sans-serif!important}
.block-container{max-width:1240px;padding-top:2.4rem}
footer{visibility:hidden}
.titulo,.h-sec,.h-card,.h-plan,.num{font-family:'Bricolage Grotesque',system-ui,sans-serif!important;color:var(--tinta)}
.titulo{font-size:2.3rem;font-weight:800;line-height:1.1}
.sub{color:var(--suave);margin:.35rem 0 1.8rem}
.h-sec{font-size:1.2rem;font-weight:700;margin-bottom:.7rem}
.h-card{font-size:1.5rem;font-weight:700}
[data-testid="stForm"]{background:#fff;border:1px solid var(--linea);border-radius:16px;padding:26px 28px}
.panel{background:#fff;border:1px solid var(--linea);border-radius:10px;padding:22px 24px;margin-bottom:16px}
.panel p,.panel li,.panel b{color:var(--tinta)!important;margin:0}
.dos-col{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:14px}
.bloque{padding:2px 0 2px 14px;border-left:4px solid var(--verde)}
.bloque.mal{border-left-color:var(--alerta)}
.bloque b{display:block;margin-bottom:6px}
.bloque ul{margin:0;padding-left:1.1rem}
.bloque li{margin-bottom:7px;line-height:1.45}
.mejoras{list-style:none;padding:0;margin:8px 0 0}
.mejoras li{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-top:1px solid var(--linea)}
.mejoras li:first-child{border-top:none}
.num{flex:0 0 40px;height:40px;border-radius:8px;background:var(--xp);font-weight:800;font-size:1.25rem;display:flex;align-items:center;justify-content:center}
.mejoras b{display:block;margin-bottom:2px}
.plan{background:var(--tinta);border-radius:18px;padding:26px 28px}
.h-plan{color:#fff!important;font-size:1.5rem;font-weight:700;margin-bottom:10px}
.fila{display:grid;grid-template-columns:90px 1fr;gap:14px;padding:13px 0;border-top:1px solid rgba(255,255,255,.18)}
.fila span{color:var(--xp);font-weight:700}
.plan p{color:#fff!important;margin:0;line-height:1.45}
[data-testid="stWidgetLabel"] p{font-weight:700;color:var(--tinta)!important}
[data-baseweb="textarea"]{background:#fff!important;border:1.5px solid var(--linea)!important;border-radius:10px!important}
[data-baseweb="textarea"]:focus-within{border-color:var(--verde)!important}
.stTextArea textarea{background:#fff!important;color:var(--tinta)!important}
.stButton>button,[data-testid="stFormSubmitButton"]>button{background:var(--verde);border:none;border-radius:10px;padding:.65rem 1.4rem;font-weight:700}
.stButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{background:#17604A}
.stButton>button:focus-visible,[data-testid="stFormSubmitButton"]>button:focus-visible{outline:3px solid var(--xp)}
.stButton>button p,[data-testid="stFormSubmitButton"]>button p{color:#fff!important}
[data-testid="stFormSubmitButton"]>button{width:100%}
@media(max-width:760px){.dos-col{grid-template-columns:1fr}.fila{grid-template-columns:1fr;gap:2px}}
"""


# ───────────────────────── Vista del informe ─────────────────────────
def mostrar_informe(inf):
    li = lambda items: "".join(f"<li>{escape(x)}</li>" for x in items)
    st.markdown(
        '<div class="panel"><div class="h-card">Semana en Revisión</div><div class="dos-col">'
        f'<div class="bloque"><b>Victorias</b><ul>{li(inf["logros"])}</ul></div>'
        f'<div class="bloque mal"><b>Desafíos</b><ul>{li(inf["desafios"])}</ul></div>'
        "</div></div>",
        unsafe_allow_html=True,
    )
    mejoras = "".join(
        f'<li><div class="num">{i}</div><div><b>{escape(m["titulo"])}</b><p>{escape(m["detalle"])}</p></div></li>'
        for i, m in enumerate(inf["mejoras"], 1)
    )
    st.markdown(
        f'<div class="panel"><div class="h-card">Mejores Mejoras</div><ol class="mejoras">{mejoras}</ol></div>',
        unsafe_allow_html=True,
    )
    p = inf["plan"]
    st.markdown(
        '<div class="plan"><div class="h-plan">Plan para la próxima semana</div>'
        f'<div class="fila"><span>Enfoque</span><p>{escape(p["enfoque"])}</p></div>'
        f'<div class="fila"><span>Meta</span><p>{escape(p["meta"])}</p></div>'
        f'<div class="fila"><span>Hábito</span><p>{escape(p["habito"])}</p></div></div>',
        unsafe_allow_html=True,
    )


# ───────────────────────── Página ─────────────────────────
st.set_page_config(page_title="Agente de Revisión", page_icon="🩺", layout="wide")
st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
st.markdown(
    '<div class="titulo">Agente de Revisión Diaria y Semanal</div>'
    '<div class="sub">Cierra el día por la noche. Los domingos, el Agente revisa tu semana.</div>',
    unsafe_allow_html=True,
)

izq, der = st.columns([5, 7], gap="large")

# ── Sección 1: Registro nocturno ──
with izq:
    st.markdown('<div class="h-sec">Registro nocturno</div>', unsafe_allow_html=True)
    with st.form("registro_nocturno", clear_on_submit=True):
        st.markdown('<div class="h-card">¿Cómo fue hoy?</div>', unsafe_allow_html=True)
        st.caption(f"Cierre del {date.today():%d/%m/%Y}")
        bien = st.text_area("¿Qué salió bien?", height=96)
        mal = st.text_area("¿Qué no salió bien?", height=96)
        lecciones = st.text_area("Lecciones aprendidas", height=96)
        gratitud = st.text_area("Gratitud", height=96)
        enviado = st.form_submit_button("Guardar en el registro", type="primary")

    if enviado:
        textos = [t.strip() for t in (bien, mal, lecciones, gratitud)]
        if not any(textos):
            st.error("Completa al menos un campo para guardar el registro.")
        else:
            guardar_registro({
                "fecha": date.today().isoformat(),
                "bien": textos[0], "mal": textos[1],
                "lecciones": textos[2], "gratitud": textos[3],
            })
            # 🔌 LLM (opcional, feedback diario): aquí puedes enviar los 4 textos al
            # modelo para evaluar qué misiones se cumplieron y mostrar un comentario
            # inmediato, por ejemplo:  st.info(feedback_del_modelo)
            st.success("Guardado en el registro. Si ya habías guardado hoy, se reemplazó ese cierre.")
    st.caption(f"{len(cargar_registros())} cierres en el registro")

# ── Sección 2: Revisión semanal ──
with der:
    st.markdown('<div class="h-sec">Revisión semanal</div>', unsafe_allow_html=True)
    if "informe" not in st.session_state:
        st.session_state.informe = INFORME_DEMO
        st.session_state.estado = "Vista de ejemplo. Genera el informe para analizar tus registros."

    if st.button("Generar informe semanal", type="primary"):
        regs = registros_ultimos_7_dias()
        with st.spinner("El Agente está leyendo tus últimos 7 días…"):
            st.session_state.informe = generar_informe_semanal(regs)  # ← aquí entra el LLM
        st.session_state.estado = (
            f"Informe basado en {len(regs)} registro(s) de los últimos 7 días."
            if regs else "Todavía no hay registros en los últimos 7 días; se muestra el ejemplo."
        )
    st.caption(st.session_state.estado)
    mostrar_informe(st.session_state.informe)
