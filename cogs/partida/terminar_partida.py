# cogs/terminar_partida.py
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from database.db_manager import finalizar_partida, obtener_partida, reset_partida
from config import ROLES

# Nombre del rol global de participante (coincide con el creado en comenzar_partida)
PARTICIPANT_ROLE_NAME = "Participante"

class TerminarPartidaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="terminar",
        description="Termina la partida, reinicia la base de datos y elimina los roles de Discord asociados."
    )
    async def terminar(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild = interaction.guild
        guild_id = guild.id

        # 1. Verificar partida activa
        partida = obtener_partida(guild_id)
        if not partida:
            return await interaction.followup.send(
                "❌ No hay ninguna partida activa en este servidor.",
                ephemeral=True
            )

        # 2. Marcar como finalizada y resetear datos
        finalizar_partida(guild_id)
        reset_partida(guild_id)

        # 3. Eliminar roles de Discord
        roles_eliminados = []
        nombres_roles = ROLES.copy() + [PARTICIPANT_ROLE_NAME]
        for nombre in nombres_roles:
            role = get(guild.roles, name=nombre)
            if role:
                try:
                    await role.delete(reason="Partida finalizada: eliminado rol")
                    roles_eliminados.append(nombre)
                except discord.Forbidden:
                    # Falta permiso para eliminar
                    pass

        # 4. Confirmación al usuario
        texto = "✅ Partida terminada y reiniciada correctamente."
        if roles_eliminados:
            texto += "\n🚮 Roles eliminados: {}".format(
                ", ".join(roles_eliminados)
            )
        else:
            texto += "\n⚠️ No se encontraron roles para eliminar."
        texto += "\n¡Puedes empezar una nueva con `/partida crear`!"

        await interaction.followup.send(texto)

async def setup(bot: commands.Bot):
    await bot.add_cog(TerminarPartidaCog(bot))
