import discord
from discord.ext import commands
from discord import app_commands

class GameInfoCog(commands.Cog):
    """
    Cog que muestra una breve descripción del juego.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="info_descripcion",
        description="Muestra una breve descripción de en qué consiste el juego."
    )
    async def descripcion(self, interaction: discord.Interaction):
        """
        Envía una breve descripción del juego.
        """
        embed = discord.Embed(
            title="🎲 Revs And Reigns",
            description=(
                "Revs And Reigns es un juego de estrategia por turnos en Discord, "
                "donde los jugadores se unen a diferentes reinos y asumen roles como Mayoral, "
                "Canciller, Comandante o Tesorero. Durante la partida, deberán coordinarse, "
                "gestionando recursos, diplomacia y combates para expandir su reino y alcanzar la victoria."
                "\n\n"
                "Las partidas de Revs And Reigns estan pensadas para durar dias. "
                "Cada accion de cada rol tiene cooldowns determinados, "
                "A lo largo de la partida, ocurriran eventos que afectaran a los reinos, "
                "y los jugadores deberan adaptarse a las circunstancias.\n\n"
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🔹 Mecánica básica",
            value=(
                "1. Se crea una partida con varios reinos.\n"
                "2. Los jugadores se registran en la lista de espera.\n"
                "3. Al comenzar, se asignan reinos y roles.\n"
                "4. Una vez comenzada la partida, los jugadores podrán empezar a tomar decisiones."
            ),
            inline=False
        )
        embed.set_footer(text="¡Que comience la conquista!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GameInfoCog(bot))
