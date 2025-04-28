import random
import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import obtener_jugador, obtener_reino
from utils.cooldown_manager import (tiene_cooldown, registrar_uso, tiempo_restante)

# Hardcodeado; luego podrás extraerlo de la BD
REINOS_DISPONIBLES = ["Eltaris", "Lunaris", "Valken", "Zendar"]

class AccionesDiplomatico(commands.GroupCog, group_name="diplomatico", group_description="Acciones para diplomáticos"):
    COOLDOWN_ESPIAR = 6 * 60 * 60  # 6 horas

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        print("⚙️  Cog AccionesDiplomatico cargado.")

    @app_commands.command(name="espiar_reino", description="Espía a un reino enemigo para obtener información")
    @app_commands.describe(nombre_reino_objetivo="El reino al que quieres espiar")
    async def espiar_reino(self,interaction: discord.Interaction,nombre_reino_objetivo: str):
        # Validar rol de diplomático
        jugador = obtener_jugador(interaction.user.id)
        if not jugador or jugador[4] != "Diplomático":
            return await interaction.response.send_message("❌ No tienes permiso para usar esto.", ephemeral=True)

        # Cooldown
        if tiene_cooldown(interaction.user.id, "espiar_reino", self.COOLDOWN_ESPIAR):
            restante = tiempo_restante(interaction.user.id, "espiar_reino", self.COOLDOWN_ESPIAR)
            h, m = divmod(restante, 3600)[0], divmod(restante % 3600, 60)[0]
            return await interaction.response.send_message(f"⌛ Espera {h}h {m}m para volver a espiar.",ephemeral=True)

        # Validar existencia de reino
        objetivo = obtener_reino(nombre_reino_objetivo)
        if not objetivo:
            return await interaction.response.send_message(f"❌ El reino “{nombre_reino_objetivo}” no existe.",ephemeral=True)

        # Resolución del espionaje
        success = random.randint(1, 100) <= 80
        if success:
            # Manda la info por DM
            await interaction.user.send(f"📜 Info secreta de **{nombre_reino_objetivo}**:\n{objetivo}")
            await interaction.response.send_message("✅ Espionaje exitoso. Revisa tu DM.",ephemeral=True)
        else:
            # Revela al canal
            await interaction.response.send_message(f"🚨 ¡{interaction.user.mention} ha sido descubierto espiando a **{nombre_reino_objetivo}**!",ephemeral=False)

        # Registrar uso para cooldown
        registrar_uso(interaction.user.id, "espiar_reino")

    @espiar_reino.autocomplete("nombre_reino_objetivo")
    async def _autocomplete_reinos(self,interaction: discord.Interaction,current: str) -> list[app_commands.Choice[str]]:
        # Devuelve hasta 25 opciones que contengan `current`
        return [app_commands.Choice(name=r, value=r) for r in REINOS_DISPONIBLES
            if current.lower() in r.lower()
        ][:25]


async def setup(bot: commands.Bot):
    await bot.add_cog(AccionesDiplomatico(bot))
