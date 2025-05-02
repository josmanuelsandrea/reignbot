import discord
from discord.ext import commands
from discord import app_commands

from config import GENERAL_ROLE_NAME, INTRO_TEXT, ROLES
from database.db_manager import asignar_reinos_y_roles, marcar_partida_en_curso, obtener_partida_esperando, registrar_accion

class StartMatchCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="comenzar_partida", description="Inicia la partida, reparte reinos y roles y crea los roles en Discord.")
    async def comenzar_partida(self, interaction: discord.Interaction):
        # 0) Deferimos para darnos más tiempo (y evitar el timeout de 3s)
        await interaction.response.defer(thinking=True)  # o deferred reply público/ephemeral

        # 1) Recuperar la partida en espera
        partida = obtener_partida_esperando(interaction.guild.id)
        if not partida:
            return await interaction.followup.send(
                "❌ No hay partida en espera para iniciar.", 
                ephemeral=True
            )

        # 2) Intentamos asignar reinos y roles
        try:
            jugadores = asignar_reinos_y_roles(partida)
        except ValueError as err:
            return await interaction.followup.send(
                f"❌ {err}", 
                ephemeral=True
            )

        marcar_partida_en_curso(partida)

        guild = interaction.guild
        # 3) Creamos (o recuperamos) roles
        from discord.utils import get

        async def get_or_create(name: str):
            role = get(guild.roles, name=name)
            return role or await guild.create_role(name=name)

        general_role = await get_or_create(GENERAL_ROLE_NAME)
        roles_map = {rol: await get_or_create(rol) for rol in ROLES}

        # 4) Asignamos roles a cada jugador
        for j in jugadores:
            try:
                member = await guild.fetch_member(j.usuario_id)
            except discord.NotFound:
                continue

            await member.add_roles(general_role)
            for jr in j.roles:
                dr = roles_map.get(jr.rol)
                if dr:
                    await member.add_roles(dr)

            registrar_accion(
                j,
                f"{j.nombre_usuario} del reino {j.reino.nombre} recibió roles: "
                f"{', '.join(r.rol for r in j.roles)}"
            )
            
        lines = INTRO_TEXT.copy()

        # 5) Construir mensaje épico
        for j in jugadores:
            roles_list = ", ".join(r.rol for r in j.roles)
            lines.append(
                f"• **{j.nombre_usuario}** del reino **{j.reino.nombre}** "
                f"asignado a ser: _{roles_list}_"
            )
        epic = "\n".join(lines)

        # 6) Enviamos el mensaje final como followup
        await interaction.followup.send(epic)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(StartMatchCog(bot))