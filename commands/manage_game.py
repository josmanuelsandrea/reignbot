import random
import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import agregar_reino, agregar_jugador
from config import NOMBRES_REINOS, TERRITORIO_TOTAL, ROLES


class ManageGame(commands.GroupCog, group_name="partida", group_description="Acciones relacionadas a la partida."):
    """
    Comandos para gestionar la partida: crear reinos y unirse a ellos.
    """

    def __init__(self, bot: commands.Bot):
        # Llamamos al init de la clase base para evitar errores internos
        super().__init__()
        self.bot = bot
        print("⚙️ Cargando GestionPartida...")

    @app_commands.command(name="crear", description="Crear una nueva partida con reinos.")
    async def crear(self, interaction: discord.Interaction):
        """
        Divide el territorio igualmente entre los reinos y los crea con valores iniciales.
        """
        territorio_por_reino = TERRITORIO_TOTAL // len(NOMBRES_REINOS)
        for nombre in NOMBRES_REINOS:
            agregar_reino(
                nombre,
                territorio_por_reino,
                soldados=100,
                oro=500,
                moral=70,
                alimentacion=70,
                defensa_base=50
            )
        await interaction.response.send_message(f"🎲 Partida creada con éxito. Reinos disponibles: {', '.join(NOMBRES_REINOS)}",ephemeral=False)

    @app_commands.command(name="unirme", description="Unirte a un reino aleatorio y recibir un rol.")
    async def unirme(self, interaction: discord.Interaction):
        """
        Asigna al usuario un reino y un rol aleatorio, y lo crea en la BD.
        """
        reino_asignado = random.choice(NOMBRES_REINOS)
        rol_asignado = random.choice(ROLES)
        agregar_jugador(interaction.user.id, str(interaction.user), reino_asignado, rol_asignado)
        await interaction.response.send_message(f"🛡️ {interaction.user.mention} se ha unido al reino {reino_asignado} como {rol_asignado}.",ephemeral=False)

async def setup(bot: commands.Bot):
    # Registra el Cog en el bot
    await bot.add_cog(ManageGame(bot))
