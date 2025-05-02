import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import encontrar_jugador

class MeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="quien_soy",
        description="Muestra información sobre ti: tu reino y tus roles en la partida."
    )
    async def me(self, interaction: discord.Interaction):
        # Busca al jugador en la BD
        jugador = encontrar_jugador(interaction.user.id)
        if jugador is None:
            return await interaction.response.send_message(
                "❌ No estás en ninguna partida.", 
                ephemeral=True
            )

        # Nombre del reino (puede ser None si algo falló)
        reino = jugador.reino.nombre if jugador.reino else "– Sin reino –"

        # Todos los roles desde la tabla intermedia JugadorRol
        roles = [jr.rol for jr in jugador.roles]
        roles_str = ", ".join(roles) if roles else "– Sin roles –"

        # Responder de forma efímera
        await interaction.response.send_message(
            f"🏰 **Reino asignado:** {reino}\n"
            f"⚔️ **Roles asignados:** {roles_str}",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(MeCog(bot))
