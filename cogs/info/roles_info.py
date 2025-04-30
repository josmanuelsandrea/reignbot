import discord
from discord.ext import commands
from discord import app_commands

from config import ROLES
from database.db_manager import obtener_reino  # opcional, si quieres más datos

ROLE_DESCRIPTIONS = {
    "Comandante": "Lider militar: dirige tropas, organiza batallas y toma decisiones estratégicas.",
    "Canciller": "Diplomacia: maneja relaciones con otros reinos, negocia tratados y alianzas.",
    "Tesorero": "Gestión financiera: controla los recursos, impuestos y gastos del reino.",
    "Mayoral": "Gobernador local: administra una ciudad o región, asegurando su desarrollo y bienestar.",
}

class RolesInfoCog(commands.Cog):
    """
    Cog que muestra información detallada de cada rol disponible en la partida.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info_roles", description="Muestra información de los roles y sus capacidades.")
    async def roles(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ℹ️ Información de los Roles",
            color=discord.Color.green()
        )
        for rol in ROLES:
            descripcion = ROLE_DESCRIPTIONS.get(
                rol, "Sin descripción disponible para este rol."
            )
            embed.add_field(
                name=rol,
                value=descripcion,
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RolesInfoCog(bot))
