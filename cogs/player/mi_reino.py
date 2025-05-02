# cogs/mi_reino.py

import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import encontrar_jugador  # tu helper
from database.models import Jugador, Reino

class MiReinoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="mi_reino",
        description="🏰 Muestra la información y estadísticas de tu reino."
    )
    async def mi_reino(self, interaction: discord.Interaction):
        # 1) Busca al jugador en la BD
        jugador: Jugador | None = encontrar_jugador(interaction.user.id)
        if not jugador or not jugador.reino:
            return await interaction.response.send_message(
                "❌ No estás asignado a ningún reino en una partida en curso.",
                ephemeral=True
            )

        reino: Reino = jugador.reino

        # 2) Construir embed con las stats del reino
        embed = discord.Embed(
            title=f"🏰 Reino **{reino.nombre}**",
            colour=discord.Colour.dark_gold()
        )
        # Asumiendo que tu modelo Reino tiene estos campos:
        embed.add_field(name="🌍 Territorio",    value=str(reino.territorio),   inline=True)
        embed.add_field(name="🛡️ Defensa",       value=str(reino.defensa_base), inline=True)
        embed.add_field(name="⚔️ Soldados",      value=str(reino.soldados),     inline=True)
        embed.add_field(name="💰 Oro",           value=str(reino.oro),          inline=True)
        embed.add_field(name="🍖 Alimentación",  value=str(reino.comida), inline=True)

        # Pie de página con recordatorio de tu usuario
        embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # 3) Enviamos de forma efímera
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(MiReinoCog(bot))
