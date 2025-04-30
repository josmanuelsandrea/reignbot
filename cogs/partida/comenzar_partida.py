# cogs/comenzar_partida.py
import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

from database.db_manager import (
    obtener_jugadores_en_espera,
    obtener_reinos,
    actualizar_jugador_completo
)
from config import ROLES

# Nombre del rol general para todos los participantes
global_participante_role = "Participante"

class ComenzarPartidaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="comenzar_partida",
        description="Distribuir jugadores a reinos, asignar roles y crear roles de Discord."
    )
    async def comenzar_partida(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        guild = interaction.guild

        # 1. Obtener datos de la base de datos
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

        # 3. Crear roles de Discord si no existen
        # Rol de participante general
        participante_role = get(guild.roles, name=global_participante_role)
        if participante_role is None:
            participante_role = await guild.create_role(name=global_participante_role)

        # Roles específicos del juego
        role_objects = {}
        for role_name in ROLES:
            role = get(guild.roles, name=role_name)
            if role is None:
                role = await guild.create_role(name=role_name)
            role_objects[role_name] = role

        # 4. Distribuir jugadores entre reinos
        distribucion = {reino: [] for reino in reinos}
        for idx, jugador in enumerate(jugadores_en_espera):
            reino_asignado = reinos[idx % len(reinos)]
            distribucion[reino_asignado].append(jugador)

        cambios = []

        # 5. Asignar roles dentro de cada reino y en Discord
        for reino, jugadores in distribucion.items():
            if not jugadores:
                continue

            roles_disponibles = ROLES.copy()
            asignaciones = {j["usuario_id"]: [] for j in jugadores}

            max_intentos = 1000
            intentos = 0

            # Asignación aleatoria de roles por rondas
            while roles_disponibles and intentos < max_intentos:
                for j in jugadores:
                    if not roles_disponibles:
                        break
                    elegir = random.randint(0, len(roles_disponibles) - 1)
                    rol = roles_disponibles.pop(elegir)
                    asignaciones[j["usuario_id"]].append(rol)
                intentos += 1

            # Guardar en DB y asignar roles de Discord
            for j in jugadores:
                usuario_id = j["usuario_id"]
                roles_texto = ", ".join(asignaciones[usuario_id])
                # Actualizar en DB
                actualizar_jugador_completo(usuario_id, reino, roles_texto)

                # Asignar roles en Discord
                try:
                    member = await guild.fetch_member(usuario_id)
                    # Añadir rol de participante
                    await member.add_roles(participante_role)
                    # Añadir cada rol específico
                    for role_name in asignaciones[usuario_id]:
                        await member.add_roles(role_objects[role_name])
                except discord.NotFound:
                    # Usuario no encontrado en el servidor, se omite
                    pass

                cambios.append(
                    f"🏰 {j['nombre_usuario']} fue asignado al Reino de **{reino}** como **{roles_texto}**."
                )

        # 6. Enviar resultado final
        if cambios:
            await interaction.followup.send(
                "✅ Partida iniciada con las siguientes asignaciones y roles en Discord:\n"
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
