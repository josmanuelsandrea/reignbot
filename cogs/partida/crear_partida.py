# cogs/crear_partida.py
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import (
    inicializar_db,
    crear_partida,
    obtener_partida,
    agregar_reino,
)

from config import TERRITORIO_TOTAL

class CrearPartidaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="crear",
        description="Crear una nueva partida en este servidor especificando los nombres de los reinos."
    )
    @app_commands.describe(
        nombres="Lista de nombres de reinos separados por comas, p.ej. 'Eltaris, Lunaris, Valken'. NOTA: los nombres seran mostrados siempre como 'Reino de <nombre>'."
    )
    async def crear(self, interaction: discord.Interaction, nombres: str):
        inicializar_db()
        guild_id = interaction.guild.id
        if obtener_partida(guild_id):
            return await interaction.response.send_message(
                "❌ Ya hay una partida activa en este servidor.", ephemeral=True
            )

        lista_nombres = [n.strip() for n in nombres.split(',') if n.strip()]
        if len(lista_nombres) < 2:
            return await interaction.response.send_message(
                "❌ Debes indicar al menos dos nombres de reinos separados por comas.", ephemeral=True
            )

        crear_partida(guild_id, "Partida de Reinos", datetime.utcnow().isoformat())
        territorio_por_reino = TERRITORIO_TOTAL // len(lista_nombres)
        for nombre in lista_nombres:
            agregar_reino(
                nombre,
                territorio_por_reino,
                soldados=100,
                oro=500,
                moral=70,
                alimentacion=70,
                defensa_base=50
            )

        await interaction.response.send_message(
            f"🎲 Partida creada con reinos: {', '.join(lista_nombres)}."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(CrearPartidaCog(bot))
