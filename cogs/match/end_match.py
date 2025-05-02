import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

from config import GENERAL_ROLE_NAME, ROLES
from database.db_manager import marcar_partida_finalizada
from database.models import Partida

class EndMatchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="terminar_partida", description="Finaliza la partida y limpia los roles de los jugadores.")
    async def terminar_partida(self, interaction: discord.Interaction):
        # 0) Deferimos para tener tiempo
        await interaction.response.defer(thinking=True)

        # 1) Buscamos la partida en curso
        from peewee import DoesNotExist
        try:
            partida = (Partida
                       .select()
                       .where(
                           (Partida.guild_id == interaction.guild.id) &
                           (Partida.estado == 'en_curso')
                       )
                       .get())
        except DoesNotExist:
            return await interaction.followup.send(
                "❌ No hay ninguna partida en curso.", ephemeral=True
            )

        guild = interaction.guild

        # 2) Preparamos la lista de roles a quitar
        general_role = get(guild.roles, name=GENERAL_ROLE_NAME)
        game_roles = [get(guild.roles, name=r) for r in ROLES]
        roles_to_remove = [r for r in ([general_role] + game_roles) if r]

        # 3) Iteramos sobre cada jugador y le quitamos solo los roles que tenga
        for jugador in partida.jugadores:
            try:
                member = await guild.fetch_member(jugador.usuario_id)
            except discord.NotFound:
                # el usuario no está en el servidor
                continue

            # filtrar solo los roles que el miembro realmente tenga
            assigned = [r for r in roles_to_remove if r in member.roles]
            if not assigned:
                continue

            try:
                # quitamos todos a la vez
                await member.remove_roles(*assigned, reason="Partida finalizada")
            except discord.HTTPException as http_err:
                # opcional: loggear o notificar que no se pudo quitar algún rol
                print(f"No pude quitar roles de {member}: {http_err}")

        # 4) Marcamos la partida como finalizada en BD
        marcar_partida_finalizada(partida)

        # 5) Mensaje de confirmación
        await interaction.followup.send(
            "🛑 Partida finalizada y roles removidos correctamente."
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(EndMatchCog(bot))