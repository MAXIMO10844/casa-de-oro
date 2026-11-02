import streamlit as st
import random
import time
import base64
import os
import unicodedata
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote

# Menú bonito (opcional): si no está instalado, usa un radio normal
try:
    from streamlit_option_menu import option_menu
    HAS_MENU = True
except Exception:
    HAS_MENU = False

# ---------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Casa de Oro - Sugerencias de la Suerte",
    page_icon="🎰",
    layout="centered",
)

NUM_TAQUILLA = "584127456048"

# ---- Rotación automática de animalitos ----
# Cada cuántas horas cambia el animalito de la suerte y el acertijo.
# Usa un número que divida 24 exacto: 3, 4, 6, 8 o 12.
HORAS_CAMBIO = 6
HORA_VE = timezone(timedelta(hours=-4))  # Hora de Venezuela

def ahora_ve():
    return datetime.now(HORA_VE)

def hoy_ve():
    return ahora_ve().date()

def bloque_actual():
    a = ahora_ve()
    return a.date().toordinal() * (24 // HORAS_CAMBIO) + a.hour // HORAS_CAMBIO

def proximo_cambio():
    a = ahora_ve()
    inicio = a.replace(hour=(a.hour // HORAS_CAMBIO) * HORAS_CAMBIO, minute=0, second=0, microsecond=0)
    return inicio + timedelta(hours=HORAS_CAMBIO)

def indice_rotativo(bloque, tam, sal):
    """Índice que cambia en cada bloque de horas y nunca repite el del bloque anterior."""
    i = random.Random(f"{bloque}{sal}").randrange(tam)
    anterior = random.Random(f"{bloque - 1}{sal}").randrange(tam)
    return (i + 1) % tam if i == anterior else i

def normalizar(t):
    t = unicodedata.normalize("NFD", t.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

# Si guardas tu flyer como "fondo.jpg" (o .png) junto a app.py, se usa de fondo
def cargar_fondo():
    for nombre, mime in (("fondo.jpg", "jpeg"), ("fondo.jpeg", "jpeg"), ("fondo.png", "png")):
        if os.path.exists(nombre):
            with open(nombre, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return (
                "background: linear-gradient(rgba(2,7,6,.86), rgba(2,7,6,.9)), "
                f"url(data:image/{mime};base64,{b64}) center/cover fixed;"
            )
    return "background: radial-gradient(circle at center, #0e2721 0%, #061411 70%, #020706 100%);"

FONDO = cargar_fondo()

# ---------------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp { __FONDO__ color: #FFF4D6; }

/* Header transparente y sin menú/footer de Streamlit */
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

h1, h2, h3, h4 {
    font-family: 'Poppins', sans-serif;
    color: #E3B23C !important;
    text-shadow: 0px 2px 6px rgba(0,0,0,.7);
}

/* Etiquetas y textos visibles */
label, .stMarkdown p, [data-testid="stWidgetLabel"] p { color: #FFF4D6 !important; }

/* Inputs */
input, div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="calendar"] {
    border-color: #E3B23C !important;
}
.stDateInput input, .stTextInput input {
    border: 2px solid #E3B23C !important;
    box-shadow: 0 0 8px rgba(227,178,60,.35) !important;
}

/* Radio dorado */
.stRadio label { color: #FFF4D6 !important; font-weight: 600; font-size: 16px; }
.stRadio div[role="radiogroup"] label > div:first-child { border-color: #E3B23C !important; }

/* Título con brillo */
@keyframes brillo {
    0%,100% { text-shadow: 0 0 8px rgba(227,178,60,.35); }
    50%     { text-shadow: 0 0 24px rgba(227,178,60,.9); }
}
.titulo { text-align:center; font-size: 46px; margin: 0; letter-spacing: 2px;
          font-weight: 800; color: #E3B23C; animation: brillo 3s ease-in-out infinite; }

/* Animaciones */
@keyframes aparece {
    from { opacity: 0; transform: translateY(22px) scale(.92); }
    to   { opacity: 1; transform: none; }
}
@keyframes flota {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-6px); }
}

/* Tarjetas de animalitos */
.animal-card {
    background: rgba(227,178,60,.07);
    border: 2px solid #E3B23C;
    padding: 16px 10px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 14px;
    box-shadow: 0 8px 25px rgba(0,0,0,.4);
    backdrop-filter: blur(8px);
    animation: aparece .6s ease both;
    transition: transform .25s, box-shadow .25s;
}
.animal-card:hover { transform: translateY(-6px) scale(1.03); box-shadow: 0 0 28px rgba(227,178,60,.55); }
.animal-emoji { font-size: 46px; line-height: 1.1; animation: flota 3s ease-in-out infinite; }
.animal-num { margin: 4px 0 0 0; font-size: 28px; font-weight: 800; color: #E3B23C; }
.animal-nom { margin: 2px 0 0 0; font-size: 16px; font-weight: 600; color: #FFF4D6; }

/* Tripleta */
.tripleta-box {
    background: rgba(37,211,102,.07);
    border: 2px solid #25D366;
    padding: 16px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 8px 25px rgba(0,0,0,.4);
    animation: aparece .6s ease both;
}
.tripleta-box .op { color:#E3B23C; font-weight:bold; font-size:13px; letter-spacing:1px; }
.tripleta-box .jugada { margin: 6px 0 0 0; color:#25D366; font-size: 20px; font-weight: 700; }

/* Banner del día */
.banner-dia {
    background: linear-gradient(135deg, rgba(227,178,60,.18), rgba(227,178,60,.04));
    border: 1px solid rgba(227,178,60,.6);
    border-radius: 18px;
    padding: 14px 18px;
    text-align: center;
    margin: 6px 0 18px 0;
    animation: aparece .8s ease both;
}
.banner-dia .peq { font-size: 12px; letter-spacing: 3px; color: #E3B23C; font-weight: 600; }
.banner-dia .gran { font-size: 24px; font-weight: 800; color: #FFF4D6; margin: 4px 0; }
.banner-dia .frase { font-size: 14px; opacity: .9; font-style: italic; }

/* Resultado grande (bola mágica, premios) */
.resultado {
    text-align:center; padding: 18px; margin-top: 12px;
    border: 2px solid #25D366; border-radius: 18px;
    background: rgba(37,211,102,.08);
    animation: aparece .6s ease both;
}
.resultado .emo { font-size: 60px; animation: flota 2.5s ease-in-out infinite; }
.resultado .txt { font-size: 22px; font-weight: 800; color: #25D366; }

/* Botones dorados */
.stButton>button {
    background: linear-gradient(135deg, #E3B23C 0%, #c4962b 100%);
    color: #0b1f1a !important;
    font-weight: 800;
    border: none;
    border-radius: 999px;
    padding: 14px 28px;
    width: 100%;
    font-size: 16px;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(227,178,60,.4);
    transition: all .3s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #f3c24d 0%, #d4a233 100%);
    transform: translateY(-2px);
    color: #0b1f1a !important;
}
.stButton>button p { color: #0b1f1a !important; }

/* Caja de la zona interactiva */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px dashed #E3B23C !important;
    border-radius: 18px;
    background: rgba(255,244,214,.04);
}

/* Bruja y bola de cristal */
@keyframes pulso {
    0%,100% { box-shadow: 0 0 30px 6px rgba(170,110,255,.55), inset 0 0 40px rgba(255,255,255,.2); }
    50%     { box-shadow: 0 0 55px 14px rgba(190,140,255,.85), inset 0 0 55px rgba(255,255,255,.35); }
}
.escena-bruja { display:flex; flex-wrap:wrap; align-items:center; justify-content:center; gap:14px; margin:10px 0 6px 0; }
.bruja { text-align:center; max-width:240px; }
.bruja .emo-bruja { font-size:110px; line-height:1; animation: flota 3.5s ease-in-out infinite; filter: drop-shadow(0 0 14px rgba(170,110,255,.6)); }
.burbuja { background: rgba(255,244,214,.96); color:#2a1a40; border-radius:18px; padding:10px 14px;
           font-weight:700; font-size:15px; margin-bottom:6px; box-shadow:0 4px 15px rgba(0,0,0,.4); }
.bola-wrap { text-align:center; }
.bola { width:270px; height:270px; border-radius:50%; margin:0 auto;
        background: radial-gradient(circle at 32% 28%, rgba(255,255,255,.55) 0%, rgba(190,150,255,.35) 18%, rgba(90,40,160,.85) 60%, rgba(30,10,70,.95) 100%);
        border:2px solid rgba(220,190,255,.5); display:grid; grid-template-columns:1fr 1fr;
        align-content:center; justify-items:center; gap:2px 0; padding:34px 38px; box-sizing:border-box;
        animation: pulso 3s ease-in-out infinite; }
.bola .item { text-align:center; animation: aparece .6s ease both; }
.bola .item:last-child:nth-child(odd) { grid-column: 1 / 3; }
.bola .item .e { font-size:40px; line-height:1.1; }
.bola .item .n { font-size:15px; font-weight:800; color:#FFF4D6; text-shadow:0 0 6px #000; }
.base-bola { width:150px; height:26px; margin:-6px auto 0 auto; background:linear-gradient(#c4962b,#7a5a12); border-radius:0 0 40px 40px; }
.chips { display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin:14px 0 4px 0; }
.chip { border:1px solid #E3B23C; border-radius:999px; padding:6px 14px; background:rgba(227,178,60,.1); font-weight:600; color:#FFF4D6; animation: aparece .6s ease both; }

iframe[title='streamlit_option_menu.option_menu'] { border-radius: 16px; }

/* Botón WhatsApp */
.btn-wa {
    background-color:#25D366; color:white !important; padding:14px 28px; border-radius:999px;
    text-decoration:none; font-weight:bold; font-size:16px;
    box-shadow:0 4px 15px rgba(37,211,102,.4); display:inline-block;
    transition: transform .2s;
}
.btn-wa:hover { transform: scale(1.05); }

/* Slot / tragamonedas */
.slot { text-align:center; font-size: 56px; font-weight: 800; color:#E3B23C; padding: 20px 0; }
</style>
"""
st.markdown(CSS.replace("__FONDO__", FONDO), unsafe_allow_html=True)

# ---------------------------------------------------------------
# DATOS
# ---------------------------------------------------------------
cls_clasicos = [
    ("0", "Delfín"), ("00", "Ballena"), ("1", "Carnero"), ("2", "Toro"),
    ("3", "Ciempiés"), ("4", "Alacrán"), ("5", "León"), ("6", "Rana"),
    ("7", "Perico"), ("8", "Ratón"), ("9", "Águila"), ("10", "Tigre"),
    ("11", "Gato"), ("12", "Caballo"), ("13", "Mono"), ("14", "Paloma"),
    ("15", "Zorro"), ("16", "Oso"), ("17", "Pavo"), ("18", "Burro"),
    ("19", "Chivo"), ("20", "Cochino"), ("21", "Gallo"), ("22", "Camello"),
    ("23", "Cebra"), ("24", "Iguana"), ("25", "Gallina"), ("26", "Vaca"),
    ("27", "Perro"), ("28", "Zamuro"), ("29", "Elefante"), ("30", "Caimán"),
    ("31", "Lapa"), ("32", "Ardilla"), ("33", "Pescado"), ("34", "Venado"),
    ("35", "Jirafa"), ("36", "Culebra"),
]

cls_guacharo = cls_clasicos + [
    ("37", "Tortuga"), ("38", "Búfalo"), ("39", "Lechuza"), ("40", "Avispa"),
    ("41", "Canguro"), ("42", "Tucán"), ("43", "Mariposa"), ("44", "Chigüire"),
    ("45", "Garza"), ("46", "Puma"), ("47", "Pavo Real"), ("48", "Puercoespín"),
    ("49", "Pereza"), ("50", "Canario"), ("51", "Pelícano"), ("52", "Pulpo"),
    ("53", "Caracol"), ("54", "Grillo"), ("55", "Oso Hormiguero"), ("56", "Tiburón"),
    ("57", "Pato"), ("58", "Hormiga"), ("59", "Pantera"), ("60", "Camaleón"),
    ("61", "Panda"), ("62", "Cachicamo"), ("63", "Cangrejo"), ("64", "Gavilán"),
    ("65", "Araña"), ("66", "Lobo"), ("67", "Avestruz"), ("68", "Jaguar"),
    ("69", "Conejo"), ("70", "Bisonte"), ("71", "Guacamaya"), ("72", "Gorila"),
    ("73", "Hipopótamo"), ("74", "Turpial"), ("75", "Guácharo"),
]

# El Guacharito Millonario: 101 animalitos (0, 00 y del 01 al 99)
cls_guacharito = [
    ("0", "Delfín"), ("00", "Ballena"), ("01", "Carnero"), ("02", "Toro"), ("03", "Ciempiés"),
    ("04", "Alacrán"), ("05", "León"), ("06", "Rana"), ("07", "Perico"), ("08", "Ratón"),
    ("09", "Águila"), ("10", "Tigre"), ("11", "Gato"), ("12", "Caballo"), ("13", "Mono"),
    ("14", "Paloma"), ("15", "Zorro"), ("16", "Oso"), ("17", "Pavo"), ("18", "Burro"),
    ("19", "Chivo"), ("20", "Cerdo"), ("21", "Gallo"), ("22", "Camello"), ("23", "Cebra"),
    ("24", "Iguana"), ("25", "Gallina"), ("26", "Vaca"), ("27", "Perro"), ("28", "Zamuro"),
    ("29", "Elefante"), ("30", "Caimán"), ("31", "Lapa"), ("32", "Ardilla"), ("33", "Pescado"),
    ("34", "Venado"), ("35", "Jirafa"), ("36", "Culebra"), ("37", "Tortuga"), ("38", "Búfalo"),
    ("39", "Lechuza"), ("40", "Avispa"), ("41", "Canguro"), ("42", "Tucán"), ("43", "Mariposa"),
    ("44", "Chigüire"), ("45", "Garza"), ("46", "Puma"), ("47", "Pavo Real"), ("48", "Puercoespín"),
    ("49", "Pereza"), ("50", "Canario"), ("51", "Pelícano"), ("52", "Pulpo"), ("53", "Caracol"),
    ("54", "Grillo"), ("55", "Oso Hormiguero"), ("56", "Tiburón"), ("57", "Pato"), ("58", "Hormiga"),
    ("59", "Pantera"), ("60", "Camaleón"), ("61", "Panda"), ("62", "Cachicamo"), ("63", "Cangrejo"),
    ("64", "Gavilán"), ("65", "Araña"), ("66", "Lobo"), ("67", "Avestruz"), ("68", "Jaguar"),
    ("69", "Conejo"), ("70", "Bisonte"), ("71", "Guacamaya"), ("72", "Gorila"), ("73", "Hipopótamo"),
    ("74", "Turpial"), ("75", "Guácharo"), ("76", "Rinoceronte"), ("77", "Pingüino"), ("78", "Antílope"),
    ("79", "Calamar"), ("80", "Murciélago"), ("81", "Cuervo"), ("82", "Cucaracha"), ("83", "Búho"),
    ("84", "Camarón"), ("85", "Hámster"), ("86", "Buey"), ("87", "Cabra"), ("88", "Erizo de Mar"),
    ("89", "Anguila"), ("90", "Hurón"), ("91", "Morrocoy"), ("92", "Cisne"), ("93", "Gaviota"),
    ("94", "Paujil"), ("95", "Escarabajo"), ("96", "Caballito de Mar"), ("97", "Loro"),
    ("98", "Cocodrilo"), ("99", "Guacharito"),
]

EMOJIS = {
    "Delfín": "🐬", "Ballena": "🐋", "Carnero": "🐏", "Toro": "🐂", "Ciempiés": "🐛",
    "Alacrán": "🦂", "León": "🦁", "Rana": "🐸", "Perico": "🦜", "Ratón": "🐭",
    "Águila": "🦅", "Tigre": "🐯", "Gato": "🐱", "Caballo": "🐴", "Mono": "🐵",
    "Paloma": "🕊️", "Zorro": "🦊", "Oso": "🐻", "Pavo": "🦃", "Burro": "🫏",
    "Chivo": "🐐", "Cochino": "🐷", "Gallo": "🐓", "Camello": "🐪", "Cebra": "🦓",
    "Iguana": "🦎", "Gallina": "🐔", "Vaca": "🐄", "Perro": "🐶", "Zamuro": "🦅",
    "Elefante": "🐘", "Caimán": "🐊", "Lapa": "🐹", "Ardilla": "🐿️", "Pescado": "🐟",
    "Venado": "🦌", "Jirafa": "🦒", "Culebra": "🐍", "Tortuga": "🐢", "Búfalo": "🐃",
    "Lechuza": "🦉", "Avispa": "🐝", "Canguro": "🦘", "Tucán": "🦜", "Mariposa": "🦋",
    "Chigüire": "🦫", "Garza": "🦢", "Puma": "🐆", "Pavo Real": "🦚", "Puercoespín": "🦔",
    "Pereza": "🦥", "Canario": "🐤", "Pelícano": "🐦", "Pulpo": "🐙", "Caracol": "🐌",
    "Grillo": "🦗", "Oso Hormiguero": "🐻", "Tiburón": "🦈", "Pato": "🦆", "Hormiga": "🐜",
    "Pantera": "🐈‍⬛", "Camaleón": "🦎", "Panda": "🐼", "Cachicamo": "🦔", "Cangrejo": "🦀",
    "Gavilán": "🦅", "Araña": "🕷️", "Lobo": "🐺", "Avestruz": "🪶", "Jaguar": "🐆",
    "Conejo": "🐰", "Bisonte": "🦬", "Guacamaya": "🦜", "Gorila": "🦍", "Hipopótamo": "🦛",
    "Turpial": "🐦", "Guácharo": "🦇",
    "Cerdo": "🐷", "Rinoceronte": "🦏", "Pingüino": "🐧", "Antílope": "🦌", "Calamar": "🦑",
    "Murciélago": "🦇", "Cuervo": "🐦", "Cucaracha": "🪳", "Búho": "🦉", "Camarón": "🦐",
    "Hámster": "🐹", "Buey": "🐂", "Cabra": "🐐", "Erizo de Mar": "🐚", "Anguila": "🐍",
    "Hurón": "🦦", "Morrocoy": "🐢", "Cisne": "🦢", "Gaviota": "🐦", "Paujil": "🦃",
    "Escarabajo": "🪲", "Caballito de Mar": "🐠", "Loro": "🦜", "Cocodrilo": "🐊", "Guacharito": "🦅",
}

def emoji_de(nombre):
    return EMOJIS.get(nombre, "🍀")

FRASES = [
    "La suerte favorece a quien se atreve. 🍀",
    "Hoy es un buen día para sonreír y probar suerte.",
    "Lo que tiene que llegar, llega en el momento justo. ✨",
    "Quien juega con alegría, siempre gana algo.",
    "Los astros hoy están de tu lado. 🔮",
    "Una buena energía vale más que mil números.",
    "Cada día trae su propio animalito de la suerte. 🐾",
]

def por_nombre(nombre):
    for n, nom in cls_clasicos:
        if nom == nombre:
            return (n, nom)
    return random.choice(cls_clasicos)

def tarjeta_animal(num, nom):
    return f"""
        <div class="animal-card">
            <div class="animal-emoji">{emoji_de(nom)}</div>
            <p class="animal-num">#{num}</p>
            <p class="animal-nom">{nom}</p>
        </div>
    """

def boton_wa(texto_boton, mensaje):
    url = f"https://wa.me/{NUM_TAQUILLA}?text={quote(mensaje)}"
    st.markdown(
        f"""<div style="text-align:center; margin-top:15px;">
              <a class="btn-wa" href="{url}" target="_blank">📲 {texto_boton}</a>
            </div>""",
        unsafe_allow_html=True,
    )

def escena_bruja(items, mensaje):
    """Dibuja la brujita con su bola de cristal; items = lista de (num, nombre) o None."""
    if items:
        contenido = "".join(
            f'<div class="item"><div class="e">{emoji_de(nom)}</div><div class="n">#{n}</div></div>'
            for n, nom in items
        )
    else:
        contenido = ('<div class="item" style="grid-column:1 / 3;">'
                     '<div class="e" style="font-size:64px;">✨</div><div class="n">¿Cuál será?</div></div>')
    return (
        '<div class="escena-bruja">'
        '<div class="bruja">'
        f'<div class="burbuja">{mensaje}</div>'
        '<div class="emo-bruja">🧙‍♀️</div>'
        '</div>'
        '<div class="bola-wrap">'
        f'<div class="bola">{contenido}</div>'
        '<div class="base-bola"></div>'
        '</div>'
        '</div>'
    )

def girar(datos, veces=16, pausa=0.07):
    """Efecto tragamonedas: muestra números/animales cambiando antes del resultado."""
    espacio = st.empty()
    for _ in range(veces):
        n, nom = random.choice(datos)
        espacio.markdown(
            f"<div class='slot'>🎰 #{n} {emoji_de(nom)}</div>", unsafe_allow_html=True
        )
        time.sleep(pausa)
    espacio.empty()

# ---------------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------------
st.markdown(
    "<div style='text-align:center; margin-bottom:2px;'>"
    "<span style='color:#E3B23C; font-size:13px; letter-spacing:6px; font-weight:600;'>BIENVENIDO A</span></div>",
    unsafe_allow_html=True,
)
st.markdown("<div class='titulo'>🍀 CASA DE ORO 🍀</div>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center; margin-top:2px;'>"
    "<span style='color:#FFF4D6; font-size:13px; letter-spacing:3px; opacity:.85;'>"
    "SUGERENCIAS Y VENTA TODOS LOS DÍAS</span></div>",
    unsafe_allow_html=True,
)
st.markdown("<hr style='border:1px solid rgba(227,178,60,.4); margin:18px 0;'>", unsafe_allow_html=True)

# Banner: animalito del día + frase
bloque = bloque_actual()
a_num, a_nom = cls_clasicos[indice_rotativo(bloque, len(cls_clasicos), "ANIMAL")]
frase_dia = FRASES[indice_rotativo(bloque, len(FRASES), "FRASE")]
proxima = proximo_cambio().strftime("%I:%M %p")
st.markdown(
    f"""
    <div class="banner-dia">
        <div class="peq">✨ ANIMALITO DE LA SUERTE ✨</div>
        <div class="gran">{emoji_de(a_nom)} #{a_num} {a_nom}</div>
        <div class="frase">“{frase_dia}”</div>
        <div class="frase" style="margin-top:6px; opacity:.65; font-size:12px;">⏰ Próximo animalito a las {proxima} (hora de Venezuela)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# NAVEGACIÓN
# ---------------------------------------------------------------
OPCIONES = ["Ruletas", "Tripleta", "Zona Interactiva", "Guacharito"]

if HAS_MENU:
    seleccion = option_menu(
        None,
        OPCIONES,
        icons=["dice-5", "trophy", "controller", "magic"],
        orientation="horizontal",
        styles={
            "container": {"padding": "4px", "background-color": "#0e2721", "border-radius": "16px"},
            "icon": {"color": "#E3B23C", "font-size": "18px"},
            "nav-link": {"color": "#FFF4D6", "font-weight": "600", "border-radius": "12px", "--hover-color": "rgba(227,178,60,0.15)"},
            "nav-link-selected": {"background-color": "#E3B23C", "color": "#0b1f1a", "font-weight": "800"},
        },
    )
else:
    seleccion = st.radio("Menú", OPCIONES, horizontal=True, label_visibility="collapsed")

# ---------------------------------------------------------------
# RULETAS
# ---------------------------------------------------------------
if seleccion == "Ruletas":
    loterias = [
        "Lotto Activo / La Granjita (0-36)",
        "Guácharo Activo (0-75)",
        "Monje Millonario (0-75 + Bonus)",
    ]
    loteria_sel = st.selectbox("🎯 Elige la Ruleta:", loterias)
    fecha_esp = st.date_input(
        "📅 Selecciona tu fecha de la suerte:",
        value=hoy_ve(), min_value=date(1940, 1, 1), max_value=date(2036, 12, 31), key="f_rul",
    )

    if st.button("✨ GENERAR MI SUGERENCIA DE LA SUERTE"):
        datos = cls_guacharo if ("Guácharo" in loteria_sel or "Monje" in loteria_sel) else cls_clasicos
        girar(datos)

        rng = random.Random(str(fecha_esp) + loteria_sel)
        pronosticos = rng.sample(datos, 4)

        st.toast("¡Buena suerte! 🍀", icon="🎰")
        st.markdown(f"### 🍀 Tus Animalitos para {loteria_sel}:")
        c1, c2 = st.columns(2)
        for i, (num, nom) in enumerate(pronosticos):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(tarjeta_animal(num, nom), unsafe_allow_html=True)

        txt = ", ".join([f"#{n} {nom}" for n, nom in pronosticos])
        msg = (f"¡Hola Casa de Oro! 🎰 Consulté la ruleta *{loteria_sel}* ({fecha_esp}) "
               f"y obtuve: {txt}. ¡Quiero jugar esto en taquilla!")
        boton_wa("Jugar en Taquilla por WhatsApp", msg)

    st.caption("🎲 Las sugerencias son generadas al azar, solo para entretenimiento.")

# ---------------------------------------------------------------
# TRIPLETA
# ---------------------------------------------------------------
elif seleccion == "Tripleta":
    st.markdown("### 🔥 Tripleta Millonaria (11 Sorteos)")
    st.markdown("_Elige tu fecha y genera combinaciones de 3 animalitos (00 al 36) para sellar tu tripleta._")
    fecha_tri = st.date_input(
        "📅 Fecha para la Tripleta:",
        value=hoy_ve(), min_value=date(1940, 1, 1), max_value=date(2036, 12, 31), key="f_tri",
    )

    if st.button("🎯 GENERAR 3 OPCIONES DE TRIPLETA"):
        girar(cls_clasicos, veces=14)
        rng = random.Random(str(fecha_tri) + "TRIPLETA_ORO")

        st.toast("¡Tus jugadas están listas! 🏆", icon="🔥")
        st.markdown("### 📋 Escoge tu jugada favorita:")
        for op in range(1, 4):
            tri = rng.sample(cls_clasicos, 3)
            tri_str = " - ".join([f"{emoji_de(nom)} #{n} {nom}" for n, nom in tri])
            st.markdown(
                f"""<div class="tripleta-box">
                        <span class="op">OPCIÓN {op}</span>
                        <p class="jugada">{tri_str}</p>
                    </div>""",
                unsafe_allow_html=True,
            )

        msg_t = (f"¡Hola Casa de Oro! 🎰 Vi las opciones de *Tripleta Millonaria* para el {fecha_tri}. "
                 "¡Quiero sellar una combinación para los 11 sorteos!")
        boton_wa("Pedir mi Tripleta por WhatsApp", msg_t)

    st.caption("🎲 Las combinaciones son generadas al azar, solo para entretenimiento.")

# ---------------------------------------------------------------
# ZONA INTERACTIVA
# ---------------------------------------------------------------
elif seleccion == "Zona Interactiva":
    st.markdown("### 🎮 Centro de Entretenimiento y Suerte")
    st.markdown("_Diviértete con nuestros minijuegos para descubrir un animalito especial._")

    juego = st.radio(
        "Elige tu modo de juego:",
        [
            "🌙 El Oráculo de los Sueños",
            "🧩 El Acertijo del Día",
            "🔮 La Bola Mágica de la Fortuna",
            "🎁 Rasca y Gana",
        ],
        label_visibility="collapsed",
    )

    with st.container(border=True):

        # ---------- 1. ORÁCULO DE LOS SUEÑOS ----------
        if "Sueños" in juego:
            st.markdown("#### 🌙 ¿Qué soñaste anoche?")

            SUENOS = {
                "✈️ Volaba alto por el cielo despejado": ["Águila", "Paloma", "Perico", "Gavilán"],
                "🌊 Estaba cruzando un río o corriendo en el agua": ["Pescado", "Delfín", "Caimán", "Ballena"],
                "🐅 Me perseguía un animal salvaje por la selva": ["Tigre", "León", "Oso", "Zorro"],
                "💰 Encontraba dinero o un objeto brillante enterrado": ["Chivo", "Gallo", "Elefante", "Camello"],
                "🦷 Se me caían los dientes o sentía debilidad": ["Ratón", "Burro", "Ciempiés", "Rana"],
                "👶 Cargaba en brazos a un bebé recién nacido": ["Gallina", "Vaca", "Gato", "Paloma"],
                "🐍 Veía una serpiente cruzando mi camino": ["Culebra", "Iguana", "Alacrán", "Caimán"],
                "🏠 Estaba mudándome o recorriendo una casa desconocida": ["Perro", "Lapa", "Ardilla", "Cochino"],
                "🔥 Había un incendio o mucho humo a mi alrededor": ["Alacrán", "Carnero", "Zamuro", "Toro"],
                "🚗 Manejaba un vehículo a toda velocidad": ["Caballo", "Venado", "Mono", "Jirafa"],
                "🌧️ Caminaba bajo una fuerte lluvia o tormenta": ["Pescado", "Rana", "Cebra", "Pavo"],
                "💍 Encontraba joyas, oro o anillos perdidos": ["Gallo", "Elefante", "Delfín", "Camello"],
            }
            sueno = st.selectbox("Selecciona la escena principal de tu sueño:", list(SUENOS.keys()))

            if st.button("🌙 Consultar Oráculo de los Sueños"):
                with st.spinner("El Oráculo interpreta tu sueño..."):
                    time.sleep(1.6)
                rng = random.Random(sueno + str(date.today()))
                nom = rng.choice(SUENOS[sueno])
                num, nom = por_nombre(nom)
                st.toast("¡El Oráculo ha hablado! 🌙", icon="✨")
                st.markdown(
                    f"""<div class="resultado">
                            <div class="emo">{emoji_de(nom)}</div>
                            <div class="txt">#{num} - {nom}</div>
                            <p style="margin:6px 0 0 0;">Tu sueño revela la energía de este animal. ¡Juégalo hoy en la taquilla!</p>
                        </div>""",
                    unsafe_allow_html=True,
                )
                boton_wa("Jugarlo por WhatsApp",
                         f"¡Hola Casa de Oro! 🌙 El Oráculo de los Sueños me dio el #{num} {nom}. ¡Quiero jugarlo!")

        # ---------- 2. ACERTIJO DEL DÍA ----------
        elif "Acertijo" in juego:
            st.markdown(f"#### 🧩 El Acertijo de la Suerte (cambia cada {HORAS_CAMBIO} horas)")

            BANCO = [
                ("Tengo trompa larga, orejas enormes y soy el más grande de la sabana.", "Elefante"),
                ("Mi cuello llega hasta las hojas más altas y tengo manchas por todo el cuerpo.", "Jirafa"),
                ("Llevo mi casa a cuestas y voy muy despacio, pero siempre llego.", "Tortuga"),
                ("Soy el rey de la selva y mi rugido se escucha a lo lejos.", "León"),
                ("Vuelo de noche sin hacer ruido y mis ojos enormes lo ven todo.", "Lechuza"),
                ("Parezco un caballo con pijama de rayas blancas y negras.", "Cebra"),
                ("Camino de lado, tengo dos pinzas y vivo cerca de la playa.", "Cangrejo"),
                ("Doy leche, tengo cuernos y en el corral me escuchan gritar mee.", "Chivo"),
                ("Soy el mejor amigo del hombre y muevo la cola cuando estoy feliz.", "Perro"),
                ("Canto al amanecer y despierto a toda la granja.", "Gallo"),
                ("Tengo ocho patas y tejo una tela para atrapar mi comida.", "Araña"),
                ("Soy un felino de rayas, vivo en la selva y todos me temen.", "Tigre"),
                ("Soy un reptil largo, no tengo patas y me arrastro por el suelo.", "Culebra"),
                ("Vivo en el mar, soy muy inteligente y me encanta saltar entre las olas.", "Delfín"),
                ("Tengo joroba, vivo en el desierto y aguanto muchos días sin tomar agua.", "Camello"),
            ]
            acertijo, correcta = BANCO[indice_rotativo(bloque_actual(), len(BANCO), "ACERTIJO")]

            st.markdown(f"**Acertijo actual** (próximo cambio a las {proximo_cambio().strftime('%I:%M %p')})")
            st.markdown(f"_“{acertijo}”_")
            resp = st.text_input("¿Qué animalito soy?")

            if st.button("🧩 Verificar Acertijo"):
                if resp.strip() == "":
                    st.warning("Escribe una respuesta para descubrir tu premio.")
                elif normalizar(resp) == normalizar(correcta):
                    premio = random.choice(cls_clasicos)
                    st.balloons()
                    st.markdown(
                        f"""<div class="resultado">
                                <div class="emo">🎉</div>
                                <div class="txt">¡Correcto, era el {correcta}!</div>
                                <p style="margin:6px 0 0 0;">Tu premio secreto de la casa es el
                                <b>{emoji_de(premio[1])} #{premio[0]} - {premio[1]}</b></p>
                            </div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(f"Casi... 😅 Pista: empieza con la letra **{correcta[0]}** y tiene {len(correcta)} letras.")

        # ---------- 3. BOLA MÁGICA ----------
        elif "Bola" in juego:
            st.markdown("#### 🔮 La Bola Mágica de la Fortuna")
            st.markdown("Toca el botón para sintonizar con la energía de los astros en este preciso instante.")
            MENSAJES = [
                "Los astros se alinean a tu favor.",
                "Una energía dorada te acompaña hoy.",
                "El destino guiña un ojo esta vez.",
                "Tu vibración está en su punto más alto.",
                "La fortuna toca a tu puerta.",
            ]
            if st.button("🔮 Revelar Energía Mágica"):
                with st.spinner("Consultando a los astros..."):
                    time.sleep(2)
                num, nom = random.choice(cls_clasicos)
                st.snow()
                st.markdown(
                    f"""<div class="resultado">
                            <div class="emo">{emoji_de(nom)}</div>
                            <div class="txt">✨ #{num} - {nom} ✨</div>
                            <p style="margin:6px 0 0 0;">{random.choice(MENSAJES)}</p>
                        </div>""",
                    unsafe_allow_html=True,
                )

        # ---------- 4. RASCA Y GANA ----------
        else:
            st.markdown("#### 🎁 Rasca y Gana")
            st.markdown("Hay 3 regalos. ¡Toca el que más te llame la atención!")
            cols = st.columns(3)
            elegido = None
            for i, c in enumerate(cols):
                if c.button("🎁", key=f"rasca_{i}"):
                    elegido = i
            if elegido is not None:
                with st.spinner("Abriendo tu regalo..."):
                    time.sleep(1.2)
                num, nom = random.choice(cls_clasicos)
                st.balloons()
                st.markdown(
                    f"""<div class="resultado">
                            <div class="emo">{emoji_de(nom)}</div>
                            <div class="txt">¡Tu regalo es #{num} - {nom}!</div>
                            <p style="margin:6px 0 0 0;">Escríbenos y cuéntanos cómo te fue. 🍀</p>
                        </div>""",
                    unsafe_allow_html=True,
                )
                boton_wa("Contarlo por WhatsApp",
                         f"¡Hola Casa de Oro! 🎁 En Rasca y Gana me salió el #{num} {nom}. ¡Quiero jugarlo!")

# ---------------------------------------------------------------
# GUACHARITO (la bruja y su bola de cristal)
# ---------------------------------------------------------------
else:
    st.markdown("### 🔮 Descubre tu dato hoy en Guacharito")
    st.markdown("_La bruja consulta su bola de cristal en El Guacharito Millonario: 101 animalitos, del 0 al 99 más el 00._")

    lugar = st.empty()
    lugar.markdown(escena_bruja(None, "¡Descubre tu dato hoy en Guacharito!"), unsafe_allow_html=True)

    cantidad = st.radio("¿Cuántos datos quieres?", [3, 4], index=1, horizontal=True)

    if st.button("🔮 CONSULTAR A LA BRUJA"):
        for _ in range(12):
            lugar.markdown(
                escena_bruja(random.sample(cls_guacharito, 4), "Mmm... veo algo en la bola... ✨"),
                unsafe_allow_html=True,
            )
            time.sleep(0.15)

        datos = random.Random(f"{bloque_actual()}GUACHARITO").sample(cls_guacharito, 4)[:cantidad]
        lugar.markdown(escena_bruja(datos, "¡Tus datos de hoy están listos! 🍀"), unsafe_allow_html=True)
        st.toast("¡La bruja ha hablado! 🔮", icon="✨")

        chips = "".join(f'<div class="chip">{emoji_de(nom)} #{n} {nom}</div>' for n, nom in datos)
        st.markdown(f'<div class="chips">{chips}</div>', unsafe_allow_html=True)

        txt = ", ".join([f"#{n} {nom}" for n, nom in datos])
        boton_wa("Jugar estos datos por WhatsApp",
                 f"¡Hola Casa de Oro! 🔮 La bruja me dio estos datos para Guacharito: {txt}. ¡Quiero jugarlos!")

    st.caption(f"🔮 La bruja renueva sus datos a las {proximo_cambio().strftime('%I:%M %p')} (hora de Venezuela). Solo para entretenimiento.")

# ---------------------------------------------------------------
# PIE DE PÁGINA
# ---------------------------------------------------------------
st.markdown("<hr style='border:1px solid rgba(227,178,60,.3); margin-top:40px;'>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:13px; opacity:.8;'>"
    "Escríbenos al <b>+58 412-7456048</b> | Casa de Oro 🍀 Juega con responsabilidad. "
    "Contenido solo para entretenimiento, +18.</p>",
    unsafe_allow_html=True,
)