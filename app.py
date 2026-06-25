import os
import requests
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import date

load_dotenv()

client = Anthropic()
hoy = date.today().strftime("%Y-%m-%d")
hoy_es = date.today().strftime("%d/%m/%Y")

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

TRADUCCIONES = {
    "suiza": "switzerland", "canadá": "canada", "canada": "canada",
    "españa": "spain", "alemania": "germany", "francia": "france",
    "holanda": "netherlands", "bélgica": "belgium", "belgica": "belgium",
    "croacia": "croatia", "marruecos": "morocco", "japón": "japan",
    "japon": "japan", "corea": "korea", "senegal": "senegal",
    "argentina": "argentina", "brasil": "brazil", "portugal": "portugal",
    "bosnia": "bosnia", "catar": "qatar", "qatar": "qatar",
    "colombia": "colombia", "panamá": "panama", "panama": "panama",
    "inglaterra": "england", "gales": "wales", "escocia": "scotland",
    "italia": "italy", "turquía": "turkey", "turquia": "turkey",
    "polonia": "poland", "dinamarca": "denmark", "noruega": "norway",
    "suecia": "sweden", "ucrania": "ukraine", "serbia": "serbia",
    "austria": "austria", "mexico": "mexico", "méxico": "mexico",
    "uruguay": "uruguay", "chile": "chile", "peru": "peru",
    "perú": "peru", "ecuador": "ecuador", "venezuela": "venezuela",
    "ghana": "ghana", "nigeria": "nigeria", "camerún": "cameroon",
    "camerun": "cameroon", "australia": "australia", "iran": "iran",
    "irán": "iran", "hungría": "hungary", "hungria": "hungary",
    "rumania": "romania", "grecia": "greece", "congo": "congo",
    "curazao": "curacao", "curaçao": "curacao",
    "costa de marfil": "ivory coast", "marfil": "ivory",
    "sudáfrica": "south africa", "sudafrica": "south africa",
    "egipto": "egypt", "túnez": "tunisia", "tunez": "tunisia",
    "argelia": "algeria", "costa rica": "costa rica",
    "república dominicana": "dominican republic",
    "nueva zelanda": "new zealand",
    "arabia saudita": "saudi arabia", "arabia": "saudi",
    "irak": "iraq", "china": "china", "india": "india",
    "estados unidos": "usa", "eeuu": "usa",
}

def obtener_partidos_hoy():
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": hoy, "timezone": "Europe/Madrid"}
    respuesta = requests.get(url, headers=HEADERS, params=params)
    return respuesta.json().get("response", [])

def obtener_convocatoria(team_id):
    url = "https://v3.football.api-sports.io/players/squads"
    params = {"team": team_id}
    respuesta = requests.get(url, headers=HEADERS, params=params)
    datos = respuesta.json().get("response", [])
    if not datos:
        return []
    jugadores = datos[0].get("players", [])
    return [f"{j['name']} ({j['position']})" for j in jugadores]

def obtener_ultimos_partidos(team_id):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"team": team_id, "last": 5}
    respuesta = requests.get(url, headers=HEADERS, params=params)
    partidos = respuesta.json().get("response", [])
    resultado = []
    for p in partidos:
        local = p["teams"]["home"]["name"]
        visitante = p["teams"]["away"]["name"]
        goles_local = p["goals"]["home"]
        goles_visitante = p["goals"]["away"]
        resultado.append(f"{local} {goles_local} - {goles_visitante} {visitante}")
    return resultado

def buscar_partido(partidos, texto):
    texto = texto.lower()
    palabras = texto.split()

    palabras_traducidas = []
    for palabra in palabras:
        if palabra in TRADUCCIONES:
            palabras_traducidas.append(TRADUCCIONES[palabra])

    if not palabras_traducidas:
        return None

    for p in partidos:
        local = p["teams"]["home"]["name"].lower()
        visitante = p["teams"]["away"]["name"].lower()
        if any(palabra in local or palabra in visitante for palabra in palabras_traducidas):
            return p
    return None

def obtener_contexto_partido(partido):
    home_id = partido["teams"]["home"]["id"]
    away_id = partido["teams"]["away"]["id"]
    home_name = partido["teams"]["home"]["name"]
    away_name = partido["teams"]["away"]["name"]

    convocatoria_home = obtener_convocatoria(home_id)
    convocatoria_away = obtener_convocatoria(away_id)
    ultimos_home = obtener_ultimos_partidos(home_id)
    ultimos_away = obtener_ultimos_partidos(away_id)

    liga = partido["league"]["name"]
    fecha = partido["fixture"]["date"][:10]
    hora = partido["fixture"]["date"][11:16]

    return f"""
DATOS DEL PARTIDO: {home_name} vs {away_name}
COMPETICIÓN: {liga}
FECHA: {fecha} {hora}h (hora Madrid)

CONVOCATORIA {home_name}:
{chr(10).join(convocatoria_home) if convocatoria_home else "No disponible"}

CONVOCATORIA {away_name}:
{chr(10).join(convocatoria_away) if convocatoria_away else "No disponible"}

ÚLTIMOS 5 PARTIDOS {home_name}:
{chr(10).join(ultimos_home) if ultimos_home else "No disponible"}

ÚLTIMOS 5 PARTIDOS {away_name}:
{chr(10).join(ultimos_away) if ultimos_away else "No disponible"}
"""

# Configuración de la página
st.set_page_config(page_title="Football Predictor", page_icon="⚽")

# Inicializar sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

if "partidos" not in st.session_state:
    st.session_state.partidos = obtener_partidos_hoy()

system = f"""Eres un experto en análisis de fútbol y pronósticos deportivos.
Hoy es {hoy_es} y el usuario está en España (zona horaria Europe/Madrid).
Cuando el usuario pregunte por un partido, recibirás datos reales de la API con la convocatoria actual de ambos equipos y sus últimos 5 partidos. Usa SIEMPRE esos datos para el pronóstico, nunca inventes jugadores ni resultados.
Tu pronóstico debe incluir:
1. Resultado probable (quién gana o empate)
2. Posibles goleadores (basándote en la convocatoria real)
3. Estimación de corners totales
4. Over/Under 2.5 goles
5. Cualquier otro dato relevante para una apuesta
Responde siempre en español y de forma clara y estructurada.
Si no recibes datos de partido, responde con normalidad como asistente de fútbol."""

# Pantalla de bienvenida o título
if not st.session_state.historial:
    st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 70vh;
            text-align: center;
        ">
            <div style="font-size: 64px">⚽</div>
            <h1 style="font-size: 2.5rem; margin: 0.5rem 0">Football Predictor</h1>
            <p style="color: gray; font-size: 1.1rem">Pronósticos deportivos con IA</p>
            <p style="color: gray; font-size: 0.9rem; margin-top: 1rem">
                Solo disponible para partidos del día de hoy
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("⚽ Football Predictor")

with st.sidebar:
    st.markdown("### ⚽ Football Predictor")
    if st.button("🗑️ Nueva conversación"):
        st.session_state.historial = []
        st.rerun()

# Mostrar historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# Input del usuario
if usuario := st.chat_input("Escribe aquí tu pregunta..."):
    with st.chat_message("user"):
        st.markdown(usuario)

    partido_encontrado = buscar_partido(st.session_state.partidos, usuario)
    contexto_añadido = ""

    if partido_encontrado:
        with st.spinner("🔍 Obteniendo datos del partido..."):
            contexto_añadido = obtener_contexto_partido(partido_encontrado)
    elif len([p for p in usuario.lower().split() if p in TRADUCCIONES]) > 0:
        st.warning("⚠️ No encontré ese partido en los partidos de hoy. Prueba con otro equipo.")

    mensaje_final = usuario
    if contexto_añadido:
        mensaje_final = f"{usuario}\n\n{contexto_añadido}"

    st.session_state.historial.append({"role": "user", "content": usuario})

    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            respuesta = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=system,
                messages=[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.historial[:-1]] +
                         [{"role": "user", "content": mensaje_final}]
            )
            texto = ""
            for bloque in respuesta.content:
                if bloque.type == "text":
                    texto += bloque.text
            st.markdown(texto)

    st.session_state.historial.append({"role": "assistant", "content": texto})