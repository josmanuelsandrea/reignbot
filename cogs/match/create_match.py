import discord
from discord.ext import commands
from discord import app_commands

from database.db_manager import crear_partida, obtener_partida_esperando
from database.models import initialize_db

class CreateMatch(commands.Cog):
    """
    Cog que maneja la creación de partidas y la asignación de reinos y roles.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Inicializa la base de datos (si no se ha hecho ya en otro lugar)
        initialize_db()  # Asegúrate de que la base de datos esté inicializada

    @app_commands.command(
        name="crear_partida",
        description="Crea una nueva partida indicando los nombres de los reinos separados por comas."
    )
    @app_commands.describe(nombres="p.ej. 'Eltaris, Lunaris, Valken'")
    async def crear_partida(
        self,
        interaction: discord.Interaction,
        nombres: str
    ):
        if obtener_partida_esperando(interaction.guild.id):
            await interaction.response.send_message(
                "Ya hay una partida en espera en este servidor.",
                ephemeral=True
            )
            return

        lista = [n.strip() for n in nombres.split(",") if n.strip()]
        partida = crear_partida(interaction.guild.id, lista)

        await interaction.response.send_message(
            f"✅ Partida creada con los reinos: **{', '.join(lista)}**\n"
            "Usa `/unirse` para entrar en la lista de espera."
        )
    
async def setup(bot: commands.Bot):
    await bot.add_cog(CreateMatch(bot))