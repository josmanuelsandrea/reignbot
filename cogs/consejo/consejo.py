import asyncio
import discord
from discord import Forbidden, app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Select, Button

from services.council_service import CouncilService
from database.db_manager import encontrar_jugador
from database.models import CouncilSession, Jugador
from config import COUNCIL_REASONS

# ── Modal para entrada extra (ej. nuevo nombre) ────────────────────────────────
class RenameModal(Modal):
    def __init__(self, jugador_id: int, razon_key: str, announce_channel: discord.TextChannel):
        super().__init__(title="Proponer nuevo nombre del reino")
        self.jugador_id = jugador_id
        self.razon_key = razon_key
        self.announce_channel = announce_channel

        self.new_name = TextInput(
            label="Nuevo nombre del reino",
            placeholder="Escribe el nombre deseado…",
            max_length=100
        )
        self.add_item(self.new_name)

    async def on_submit(self, interaction: discord.Interaction):
        jugador = encontrar_jugador(self.jugador_id)
        reino = jugador.reino
        cfg = COUNCIL_REASONS[self.razon_key]

        # Crear sesión
        session = CouncilService.create_session(
            reino, self.razon_key, cfg["require_all"], new_value=self.new_name.value
        )

        # Confirmación en canal
        await interaction.response.send_message(
            f"🛎️ Consejo convocado para **{cfg['label']}**.\n"
            f"Nuevo nombre: **{self.new_name.value}**\n"
            "He enviado las DMs para votar.",
            ephemeral=True
        )

        # Envío de DMs
        view = VoteView(session.id, interaction.channel)
        for miembro in Jugador.select().where(Jugador.reino == reino):
            try:
                user = await interaction.client.fetch_user(miembro.usuario_id)
                await user.send(
                    f"🗳️ **Consejo » {cfg['label']}**\n"
                    f"Reino actual: **{reino.nombre}**\n"
                    f"Nuevo nombre propuesto: **{self.new_name.value}**\n"
                    "Vota **✅ Sí** o **❌ No**",
                    view=view
                )
            except Forbidden:
                print(f"[DM] Forbidden: no pude enviar a {miembro.usuario_id}")
            except Exception as e:
                print(f"[DM] Error enviando a {miembro.usuario_id}: {e}")

        # Programar cierre automático
        CouncilService.schedule_auto_close(
            session, interaction.channel, interaction.client.loop
        )


# ── Select para lanzar el modal o crear sesión directa ─────────────────────────
class ReasonSelect(Select):
    def __init__(self, announce_channel: discord.TextChannel):
        options = [
            discord.SelectOption(label=data["label"], value=key)
            for key, data in COUNCIL_REASONS.items()
        ]
        super().__init__(
            placeholder="Selecciona razón…",
            min_values=1,
            max_values=1,
            options=options
        )
        self.announce_channel = announce_channel

    async def callback(self, interaction: discord.Interaction):
        razon = self.values[0]
        cfg = COUNCIL_REASONS[razon]
        jugador = encontrar_jugador(interaction.user.id)
        reino = jugador.reino

        # Input extra para renombrar
        if razon == "renombrar":
            await interaction.response.send_modal(
                RenameModal(interaction.user.id, razon, interaction.channel)
            )
            return

        # Crear sesión directa
        session = CouncilService.create_session(
            reino, razon, cfg["require_all"]
        )
        await interaction.response.edit_message(
            content=f"🛎️ Consejo convocado para **{cfg['label']}**.\nHe enviado las DMs para votar.",
            view=None
        )

        # Envío de DMs
        view = VoteView(session.id, interaction.channel)
        for miembro in Jugador.select().where(Jugador.reino == reino):
            try:
                user = await interaction.client.fetch_user(miembro.usuario_id)
                await user.send(
                    f"🗳️ **Consejo » {cfg['label']}**\n"
                    "Vota **✅ Sí** o **❌ No**",
                    view=view
                )
            except Forbidden:
                print(f"[DM] Forbidden: no pude enviar a {miembro.usuario_id}")
            except Exception as e:
                print(f"[DM] Error enviando a {miembro.usuario_id}: {e}")

        # Programar cierre automático
        CouncilService.schedule_auto_close(
            session, interaction.channel, interaction.client.loop
        )


# ── Vista de votos con cierre anticipado ────────────────────────────────────────
class VoteView(View):
    def __init__(self, session_id: int, announce_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.session_id = session_id
        self.announce_channel = announce_channel

    @discord.ui.button(
        label="✅ Sí",
        style=discord.ButtonStyle.success,
        custom_id="vote_yes"
    )
    async def yes(self, interaction: discord.Interaction, button: Button):
        # Registra el voto
        added = CouncilService.add_vote(self.session_id, interaction.user.id, True)
        if not added:
            return await interaction.response.send_message(
                "⚠️ Ya has votado.", ephemeral=True
            )
        await interaction.response.send_message("✅ Voto registrado.", ephemeral=True)

        # Cierre anticipado si aprobado
        if CouncilService.is_approved(CouncilSession.get_by_id(self.session_id)):
            await CouncilService.close_session(
                CouncilSession.get_by_id(self.session_id),
                self.announce_channel,
                delay=0
            )

    @discord.ui.button(
        label="❌ No",
        style=discord.ButtonStyle.danger,
        custom_id="vote_no"
    )
    async def no(self, interaction: discord.Interaction, button: Button):
        added = CouncilService.add_vote(self.session_id, interaction.user.id, False)
        if not added:
            return await interaction.response.send_message(
                "⚠️ Ya has votado.", ephemeral=True
            )
        await interaction.response.send_message("✅ Voto registrado.", ephemeral=True)

        if CouncilService.is_approved(CouncilSession.get_by_id(self.session_id)):
            await CouncilService.close_session(
                CouncilSession.get_by_id(self.session_id),
                self.announce_channel,
                delay=0
            )


# ── Cog principal que dispara el Select ────────────────────────────────────────
class ConsejoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="convocar_consejo",
        description="Convoca un consejo de reino y abre sesión de votación."
    )
    async def convocar(self, interaction: discord.Interaction):
        jugador = encontrar_jugador(interaction.user.id)
        if not jugador or not jugador.reino:
            return await interaction.response.send_message(
                "❌ No perteneces a ningún reino activo.", ephemeral=True
            )

        view = View(timeout=60)
        view.add_item(ReasonSelect(interaction.channel))
        await interaction.response.send_message(
            "🗳️ **Selecciona la razón del consejo:**", view=view, ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ConsejoCog(bot))
