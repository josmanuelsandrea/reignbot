import discord
from discord.ext import commands
from discord import app_commands

from database.db_manager import agregar_jugador_espera, obtener_partida_esperando

class JoinMatchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(
        name="unirse",
        description="Únete a la partida en espera."
    )
    async def unirse(self, interaction: discord.Interaction):
        partida = obtener_partida_esperando(interaction.guild.id)
        if not partida:
            await interaction.response.send_message(
                "❌ No hay ninguna partida en espera. Crea una con `/crear_partida`.",
                ephemeral=True
            )
            return

        jugador = agregar_jugador_espera(
            partida,
            interaction.user.id,
            str(interaction.user)
        )
        if not jugador:
            await interaction.response.send_message(
                "⚠️ Ya estás en la lista de espera para esta partida.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"✅ Te has unido a la partida (ID {partida.id}).",
            ephemeral=True
        )
        
async def setup(bot: commands.Bot):
    await bot.add_cog(JoinMatchCog(bot))