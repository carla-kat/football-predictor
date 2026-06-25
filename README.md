# ⚽ Football Predictor

Chatbot de pronósticos deportivos con IA que analiza partidos de fútbol usando datos reales y genera predicciones completas. Disponible en versión terminal y versión web con interfaz Streamlit.

## 🚀 Funcionalidades

- Interfaz web de chat con Streamlit
- Versión CLI para la terminal
- Detección automática de equipos desde lenguaje natural
- Convocatoria real de ambos equipos vía API-Football
- Últimos 5 partidos de cada equipo
- Pronóstico completo: resultado probable, goleadores, corners, over/under y más
- Fecha y hora del partido en hora española
- Botón para limpiar el historial y empezar una conversación nueva
- Solo disponible para partidos del día de hoy

## 🛠️ Tecnologías

- Python 3
- [Anthropic API](https://www.anthropic.com)
- [API-Football](https://www.api-football.com)
- Streamlit
- python-dotenv
- requests

## ⚙️ Instalación

1. Clona el repositorio
2. Instala las dependencias: `pip install anthropic python-dotenv requests streamlit`
3. Crea un archivo `.env` con tus claves
4. Ejecuta la versión web: `streamlit run app.py`
5. O ejecuta la versión terminal: `python main.py`

## ⚠️ Aviso

Los pronósticos son orientativos y se generan con datos reales pero no garantizan resultados. Úsalos con responsabilidad.