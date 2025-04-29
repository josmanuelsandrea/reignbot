import random
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands

from database.db_manager import (
    inicializar_db,
    crear_partida,
    obtener_partida,
    agregar_reino,
    agregar_jugador,
    obtener_reinos,
    obtener_jugador,
    obtener_jugadores_en_espera,
    actualizar_jugador_completo
)
from config import TERRITORIO_TOTAL, ROLES


class ManageGame(commands.GroupCog,
                 group_name="partida",
                 group_description="Acciones relacionadas a la partida."):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(
        name="crear",
        description="Crear una nueva partida en este servidor especificando los nombres de los reinos."
    )
    @app_commands.describe(
        nombres="Lista de nombres de reinos separados por comas, p.ej. 'Eltaris, Lunaris, Valken'"
    )
    async def crear(self, interaction: discord.Interaction, nombres: str):
        guild_id = interaction.guild.id
        inicializar_db()
        if obtener_partida(guild_id):
            return await interaction.response.send_message(
                "❌ Ya hay una partida activa en este servidor.", ephemeral=True
            )
        lista_nombres = [n.strip() for n in nombres.split(',') if n.strip()]
        if len(lista_nombres) < 2:
            return await interaction.response.send_message(
                "❌ Debes indicar al menos dos nombres de reinos separados por comas.", ephemeral=True
            )
        fecha_inicio = datetime.utcnow().isoformat()
        crear_partida(guild_id, "Partida de Reinos", fecha_inicio)
        territorio_por_reino = TERRITORIO_TOTAL // len(lista_nombres)
        for nombre_reino in lista_nombres:
            agregar_reino(
                nombre_reino,
                territorio_por_reino,
                soldados=100,
                oro=500,
                moral=70,
                alimentacion=70,
                defensa_base=50
            )
        await interaction.response.send_message(
            f"🎲 Partida creada con reinos: {', '.join(lista_nombres)}.",
            ephemeral=False
        )

    @app_commands.command(
        name="unirme",
        description="Registrarte en la lista de espera para la partida."
    )
    async def unirme(self, interaction: discord.Interaction):
        existente = obtener_jugador(interaction.user.id)
        if existente:
            return await interaction.response.send_message(
                "❌ Ya estás registrado en la partida.", ephemeral=True
            )
        agregar_jugador(
            interaction.user.id,
            str(interaction.user),
            reino=None,
            rol=None
        )
        await interaction.response.send_message(
            f"📝 {interaction.user.mention}, has sido añadido a la lista de espera.",
            ephemeral=False
        )

    @app_commands.command(
        name="comenzar_partida",
        description="Distribuir jugadores a reinos y asignar roles."
    )
    async def comenzar_partida(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        jugadores_en_espera = obtener_jugadores_en_espera()
        reinos = [r['nombre'] for r in obtener_reinos()]

        if not jugadores_en_espera:
            return await interaction.followup.send(
                "❌ No hay jugadores en la lista de espera.", ephemeral=True
            )
        if not reinos:
            return await interaction.followup.send(
                "❌ No hay reinos disponibles. Usa `/partida crear` primero.", ephemeral=True
            )

        distribucion = {reino: [] for reino in reinos}
        for idx, jugador in enumerate(jugadores_en_espera):
            reino_asignado = reinos[idx % len(reinos)]
            distribucion[reino_asignado].append(jugador)

        cambios = []

        for reino, jugadores in distribucion.items():
            if not jugadores:
                continue

            roles_disponibles = ROLES.copy()
            asignaciones = {jugador['usuario_id']: [] for jugador in jugadores}

            max_intentos = 1000
            intentos = 0

            while roles_disponibles and intentos < max_intentos:
                for jugador in jugadores:
                    if not roles_disponibles:
                        break
                    rol = roles_disponibles.pop(random.randint(0, len(roles_disponibles) - 1))
                    asignaciones[jugador['usuario_id']].append(rol)
                intentos += 1

            for jugador in jugadores:
                roles_texto = ", ".join(asignaciones[jugador['usuario_id']])
                actualizar_jugador_completo(
                    jugador['usuario_id'],
                    reino,
                    roles_texto
                )
                cambios.append(f"🏰 {jugador['nombre_usuario']} fue asignado al reino **{reino}** como **{roles_texto}**.")

        if cambios:
            await interaction.followup.send(
                "✅ Partida iniciada con las siguientes asignaciones:\n" + "\n".join(cambios),
                ephemeral=False
            )
        else:
            await interaction.followup.send(
                "✅ Todos los roles ya estaban asignados. ¡La partida puede comenzar!",
                ephemeral=False
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(ManageGame(bot))
