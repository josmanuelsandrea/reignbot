# cogs/comenzar_partida.py
import random
import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import (
    obtener_jugadores_en_espera,
    obtener_reinos,
    actualizar_jugador_completo
)
from config import ROLES

class ComenzarPartidaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="comenzar_partida",
        description="Distribuir jugadores a reinos y asignar roles."
    )
    async def comenzar_partida(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        # 1. Obtener datos
        jugadores_en_espera = obtener_jugadores_en_espera()
        reinos = [r["nombre"] for r in obtener_reinos()]

        # 2. Validaciones
        if not jugadores_en_espera:
            return await interaction.followup.send(
                "❌ No hay jugadores en la lista de espera.",
                ephemeral=True
            )
        if not reinos:
            return await interaction.followup.send(
                "❌ No hay reinos disponibles. Usa `/partida crear` primero.",
                ephemeral=True
            )

        # 3. Distribuir jugadores entre reinos
        distribucion = {reino: [] for reino in reinos}
        for idx, jugador in enumerate(jugadores_en_espera):
            reino_asignado = reinos[idx % len(reinos)]
            distribucion[reino_asignado].append(jugador)

        cambios = []

        # 4. Asignar roles dentro de cada reino
        for reino, jugadores in distribucion.items():
            if not jugadores:
                continue

            roles_disponibles = ROLES.copy()
            asignaciones = {j["usuario_id"]: [] for j in jugadores}

            max_intentos = 1000
            intentos = 0

            # Mientras queden roles y no superemos los intentos máximos,
            # asignamos un rol aleatorio a cada jugador por ronda.
            while roles_disponibles and intentos < max_intentos:
                for j in jugadores:
                    if not roles_disponibles:
                        break
                    elegir = random.randint(0, len(roles_disponibles) - 1)
                    rol = roles_disponibles.pop(elegir)
                    asignaciones[j["usuario_id"]].append(rol)
                intentos += 1

            # 5. Guardar en base de datos y preparar mensajes
            for j in jugadores:
                roles_texto = ", ".join(asignaciones[j["usuario_id"]])
                actualizar_jugador_completo(
                    j["usuario_id"],
                    reino,
                    roles_texto
                )
                cambios.append(
                    f"🏰 {j['nombre_usuario']} fue asignado al reino **{reino}** como **{roles_texto}**."
                )

        # 6. Enviar resultado final
        if cambios:
            await interaction.followup.send(
                "✅ Partida iniciada con las siguientes asignaciones:\n"
                + "\n".join(cambios),
                ephemeral=False
            )
        else:
            await interaction.followup.send(
                "✅ Todos los roles ya estaban asignados. ¡La partida puede comenzar!",
                ephemeral=False
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(ComenzarPartidaCog(bot))
