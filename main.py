import os
import requests
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import date

load_dotenv()

client = Anthropic()
historial = []
hoy = date.today().strftime("%Y-%m-%d")
hoy_es = date.today().strftime("%d/%m/%Y")

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

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

def formatear_partidos(partidos):
    if not partidos:
        return "No hay partidos disponibles para hoy."
    resultado = ""
    for p in partidos:
        equipos = p["teams"]
        liga = p["league"]
        hora = p["fixture"]["date"][11:16]
        resultado += f"- {equipos['home']['name']} vs {equipos['away']['name']} ({liga['name']}) — {hora}h\n"
    return resultado

TRADUCCIONES = {
    "suiza": "switzerland",
    "canadá": "canada",
    "canada": "canada",
    "españa": "spain",
    "alemania": "germany",
    "francia": "france",
    "holanda": "netherlands",
    "países bajos": "netherlands",
    "bélgica": "belgium",
    "belgica": "belgium",
    "croacia": "croatia",
    "marruecos": "morocco",
    "japón": "japan",
    "japon": "japan",
    "corea": "korea",
    "senegal": "senegal",
    "argentina": "argentina",
    "brasil": "brazil",
    "portugal": "portugal",
    "bosnia": "bosnia",
    "catar": "qatar",
    "qatar": "qatar",
    "colombia": "colombia",
    "panamá": "panama",
    "panama": "panama",
}

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

    print(f"\n🔍 Obteniendo datos de {home_name} y {away_name}...")

    convocatoria_home = obtener_convocatoria(home_id)
    convocatoria_away = obtener_convocatoria(away_id)
    ultimos_home = obtener_ultimos_partidos(home_id)
    ultimos_away = obtener_ultimos_partidos(away_id)

    contexto = f"""
DATOS DEL PARTIDO: {home_name} vs {away_name}

CONVOCATORIA {home_name}:
{chr(10).join(convocatoria_home) if convocatoria_home else "No disponible"}

CONVOCATORIA {away_name}:
{chr(10).join(convocatoria_away) if convocatoria_away else "No disponible"}

ÚLTIMOS 5 PARTIDOS {home_name}:
{chr(10).join(ultimos_home) if ultimos_home else "No disponible"}

ÚLTIMOS 5 PARTIDOS {away_name}:
{chr(10).join(ultimos_away) if ultimos_away else "No disponible"}
"""
    return contexto

print("""
⚽ ================================= ⚽
      FOOTBALL PREDICTOR
      Pronósticos deportivos con IA
⚽ ================================= ⚽

Puedo ayudarte con:
  • Pronósticos de partidos de hoy
  • Análisis de convocatorias reales
  • Estimación de corners y goles
  • Recomendaciones de apuesta

Escribe el nombre de dos equipos y
te haré un análisis completo.
Escribe 'salir' para terminar.

⚽ ================================= ⚽
""")
partidos = obtener_partidos_hoy()
resumen_partidos = formatear_partidos(partidos)

system = f"""Eres un experto en análisis de fútbol y pronósticos deportivos.
Hoy es {hoy_es} y el usuario está en España (zona horaria Europe/Madrid).
Estos son los partidos de fútbol disponibles hoy:
{resumen_partidos}
Cuando el usuario pregunte por un partido, recibirás datos reales de la API con la convocatoria actual de ambos equipos y sus últimos 5 partidos. Usa SIEMPRE esos datos para el pronóstico, nunca inventes jugadores ni resultados.
Tu pronóstico debe incluir:
1. Resultado probable (quién gana o empate)
2. Posibles goleadores (basándote en la convocatoria real)
3. Estimación de corners totales
4. Over/Under 2.5 goles
5. Cualquier otro dato relevante para una apuesta
Responde siempre en español y de forma clara y estructurada."""

while True:
    usuario = input("Tú: ")

    if usuario.lower() == "salir":
        print("¡Hasta luego!")
        break

    partido_encontrado = buscar_partido(partidos, usuario)

    if partido_encontrado:
        contexto = obtener_contexto_partido(partido_encontrado)
        mensaje_con_contexto = f"{usuario}\n\n{contexto}"
        historial.append({"role": "user", "content": mensaje_con_contexto})
    else:
        historial.append({"role": "user", "content": usuario})

    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=system,
        messages=historial
    )

    texto = ""
    for bloque in respuesta.content:
        if bloque.type == "text":
            texto += bloque.text

    historial.append({"role": "assistant", "content": texto})
    print(f"\nClaude: {texto}\n")