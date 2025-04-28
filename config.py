import os
from dotenv import load_dotenv

# Cargar el .env
load_dotenv()

# Variables de entorno
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')  # Por defecto "!" si no está definido

TERRITORIO_TOTAL = 100000  # Total km² para repartir entre reinos
NOMBRES_REINOS = ["Eltaris", "Lunaris", "Valken", "Zendar"]
ROLES = ["General", "Espía", "Comerciante", "Granjero", "Arquitecto"]