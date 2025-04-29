# cogs/unirme.py
import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import obtener_jugador, agregar_jugador

class UnirmeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="unirme",
        description="Registrarte en la lista de espera para la partida."
    )
    async def unirme(self, interaction: discord.Interaction):
        if obtener_jugador(interaction.user.id):
            return await interaction.response.send_message(
                "❌ Ya estás registrado en la partida.", ephemeral=True
            )

        agregar_jugador(
            interaction.user.id,
            str(interaction.user),
            reino=None,
            rol=None
        )
        await interaction.response.send_message(
            f"📝 {interaction.user.mention}, has sido añadido a la lista de espera."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(UnirmeCog(bot))
