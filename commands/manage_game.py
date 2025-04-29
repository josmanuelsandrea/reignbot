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
    obtener_jugadores_por_reino,
    obtener_jugador
)
from config import TERRITORIO_TOTAL, ROLES


class ManageGame(commands.GroupCog,
                 group_name="partida",
                 group_description="Acciones relacionadas a la partida."):
    """
    Comandos para gestionar partidas por servidor, permitiendo definir nombres de reinos.
    """

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
        """
        Crea una partida única para la guild usando los nombres proporcionados.
        """
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
        description="Unirte a un reino aleatorio y recibir un rol, único por reino."
    )
    async def unirme(self, interaction: discord.Interaction):
        """
        Asigna al usuario a un reino y rol aleatorios existentes en la partida,
        asegurando que no se repita un rol dentro del mismo reino y que no se una dos veces.
        """
        # Verificar que el usuario no esté ya registrado
        existente = obtener_jugador(interaction.user.id)
        if existente:
            return await interaction.response.send_message(
                f"❌ Ya estás unido al reino **{existente['reino']}** como **{existente['rol']}**.",
                ephemeral=True
            )

        reinos = [r['nombre'] for r in obtener_reinos()]
        if not reinos:
            return await interaction.response.send_message(
                "❌ No hay reinos disponibles. Usa `/partida crear` primero.",
                ephemeral=True
            )
        reinos_disponibles = []
        for reino in reinos:
            jugadores = obtener_jugadores_por_reino(reino)
            used_roles = [j['rol'] for j in jugadores]
            available_roles = [role for role in ROLES if role not in used_roles]
            if available_roles:
                reinos_disponibles.append((reino, available_roles))
        if not reinos_disponibles:
            return await interaction.response.send_message(
                "❌ Todos los roles están ocupados en cada reino. No hay espacio disponible.",
                ephemeral=True
            )
        reino_asignado, roles_libres = random.choice(reinos_disponibles)
        rol_asignado = random.choice(roles_libres)
        agregar_jugador(
            interaction.user.id,
            str(interaction.user),
            reino_asignado,
            rol_asignado
        )
        await interaction.response.send_message(
            f"🛡️ {interaction.user.mention} se ha unido al reino {reino_asignado} como {rol_asignado}.",
            ephemeral=False
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ManageGame(bot))
