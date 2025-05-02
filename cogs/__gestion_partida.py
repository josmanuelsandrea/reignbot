# cogs/gestion_partida.py

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from database.db_manager import (
    init_db,
    crear_partida,
    obtener_partida_esperando,
    agregar_jugador_espera,
    asignar_reinos_y_roles,
    marcar_partida_en_curso,
    marcar_partida_finalizada,
    registrar_accion
)
from config import GENERAL_ROLE_NAME, ROLES, INTRO_TEXT
from database.models import Partida
from utils.discord import get_or_create_role  # p.ej. "RevsAndReigns_Player"

class GestionPartida(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        init_db()


async def setup(bot: commands.Bot):
    await bot.add_cog(GestionPartida(bot))
