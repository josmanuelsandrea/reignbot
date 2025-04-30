import discord
from discord.ext import commands
from discord import app_commands

from database.db_manager import obtener_jugador

class InfoPartidaCog(commands.Cog):
    """
    Cog que muestra al usuario su reino y rol asignados en la partida.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="info",
        description="Muestra tu reino y rol asignados en la partida."
    )
    async def info(self, interaction: discord.Interaction):
        # Obtener datos del jugador
        jugador = obtener_jugador(interaction.user.id)

        # Validar si está en una partida
        if not jugador or jugador[3] is None:
            return await interaction.response.send_message(
                "❌ No estás registrado en ninguna partida activa.",
                ephemeral=True
            )

        # El campo 'jugador' viene como tuple: (id, usuario_id, nombre_usuario, reino, rol, es_rey)
        _, _, nombre_usuario, reino, rol, _ = jugador
        rol_texto = rol or "Sin rol asignado"

        # Enviar respuesta privada
        await interaction.response.send_message(
            f"🏷️ **Reino:** {reino}\n🎭 **Rol:** {rol_texto}",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(InfoPartidaCog(bot))
