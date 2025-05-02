# cogs/cleanup_roles.py

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from config import ROLES, GENERAL_ROLE_NAME

class CleanupRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="limpiar_roles",
        description="🗑️ Elimina todos los roles de RevsAndReigns (juego y general)."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def limpiar_roles(self, interaction: discord.Interaction):
        # defer para evitar timeouts
        await interaction.response.defer(thinking=True)

        guild = interaction.guild
        names_to_remove = set(ROLES) | {GENERAL_ROLE_NAME}
        roles_to_delete = [r for r in guild.roles if r.name in names_to_remove]

        deleted = []
        for role in roles_to_delete:
            try:
                await role.delete(reason="Limpieza de roles tras finalizar partida")
                deleted.append(role.name)
            except discord.Forbidden:
                # Sin permisos para borrar ese rol
                continue
            except Exception as e:
                print(f"Error eliminando rol {role.name}: {e}")

        if deleted:
            await interaction.followup.send(
                f"✅ Roles eliminados: {', '.join(deleted)}"
            )
        else:
            await interaction.followup.send(
                "ℹ️ No se encontraron roles de juego o rol general para eliminar."
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(CleanupRoles(bot))
