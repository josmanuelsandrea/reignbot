import os
from dotenv import load_dotenv

# Cargar el .env
load_dotenv()

# Variables de entorno
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')  # Por defecto "!" si no está definido

TERRITORIO_TOTAL = 100000  # Total km² para repartir entre reinos
NOMBRES_REINOS = ["Eltaris", "Lunaris", "Valken", "Zendar"]
ROLES = ["Comandante", "Canciller", "Tesorero", "Mayoral"]
GENERAL_ROLE_NAME = "RevPlayer"

INTRO_TEXT = [
    "📜 Al principio, sólo un susurro recorrió los valles: el imperio ingobernable se había desvanecido como sueño febril. 🌬️",
    "",
    "⚜️ Luego, los nobles se alzaron: estandartes de lino ajados ondeando en la brisa, promesas de un poder renacido. 👑",
    "",
    "👤 Poco a poco, caballeros de acero y sombra respondieron a la llamada, sus armaduras reflejando la tenue luz del crepúsculo. 🌑",
    "",
    "📢 Con cada paso, el silencio cedía ante el estruendo de espadas chocando y juramentos atronadores. 🔥",
    "",
    "⏳ La tensión se enraizó en bosques y fortalezas, pues en el horizonte ya palpitaba la contienda definitiva. 💥",
    "",
    "📢 Y entonces, en un rugido ancestral, los reinos forjados en traición y ambición emergieron, listos para desafiar el destino con furia desatada. ⚡",
    "",
    "**Participantes de la contienda:**",
    "",
]

REIGN_START_PROPS = {
    "soldados": 100, # might be infinite aswell
    "oro": 500, # might be infinite max
    "comida": 70, # might be infinite
    "defensa_base": 50, # 1 - 1000
}