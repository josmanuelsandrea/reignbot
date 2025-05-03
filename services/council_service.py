from typing import Optional, Dict, Any, Tuple
import asyncio
import discord
from database.db_manager import encontrar_jugador
from database.models import CouncilSession, CouncilVote, Jugador
from config import COUNCIL_REASONS
from utils.path_utils import get_council_image_path

class CouncilService:
    """
    Servicio interno para manejar sesiones de consejo, votos y resultados.
    """
    @staticmethod
    def create_session(
        reino,
        razon_key: str,
        require_all: bool,
        new_value: Optional[str] = None
    ) -> CouncilSession:
        """
        Crea una nueva sesión de consejo.
        """
        session = CouncilSession.create(
            reino=reino,
            razon=razon_key,
            require_all=require_all,
            new_value=new_value
        )
        return session

    @staticmethod
    def add_vote(session_id: int, usuario_id: int, decision: bool) -> bool:
        """
        Registra un voto para una sesión. Devuelve False si ya existe voto.
        """
        session = CouncilSession.get_by_id(session_id)
        jugador = encontrar_jugador(usuario_id)
        # Verificar voto duplicado
        exists = CouncilVote.select().where(
            (CouncilVote.session == session) &
            (CouncilVote.jugador == jugador)
        ).exists()
        if exists:
            return False

        CouncilVote.create(session=session, jugador=jugador, decision=decision)
        return True

    @staticmethod
    def tally(session: CouncilSession) -> Tuple[int, int, int]:
        """
        Devuelve un tuple (afirmativos, negativos, total_sesión).
        """
        votos = list(CouncilVote.select().where(CouncilVote.session == session))
        afirm = sum(1 for v in votos if v.decision)
        neg = len(votos) - afirm
        total = Jugador.select().where(Jugador.reino == session.reino).count()
        return afirm, neg, total

    @staticmethod
    def is_approved(session: CouncilSession) -> bool:
        """
        Determina si la sesión está aprobada según quórum.
        """
        afirm, neg, total = CouncilService.tally(session)
        if session.require_all:
            return afirm == total
        return afirm > neg

    @staticmethod
    async def close_session(
        session: CouncilSession,
        announce_channel: discord.TextChannel,
        delay: Optional[int] = 24 * 3600
    ):
        # 1) Espera el tiempo para cerrar
        await asyncio.sleep(delay)

        # 2) Refresca estado
        session = CouncilSession.get_by_id(session.id)
        if session.closed:
            return
        session.closed = True
        session.save()

        # 3) Cálculo de resultados
        afirm, neg, total = CouncilService.tally(session)
        aprobado = CouncilService.is_approved(session)

        # 4) Si es renombrar, actualiza el nombre del reino y guarda old_name/new_name
        old_name = session.reino.nombre
        new_name = session.new_value or ""
        if aprobado and session.razon == "renombrar":
            reino = session.reino
            reino.nombre = new_name
            reino.save()

        # 5) Toma la plantilla de mensaje y formatea
        tpl     = COUNCIL_REASONS[session.razon]["success_message"]
        mensaje = tpl.format(old_name=old_name, new_name=new_name)
        embed   = discord.Embed(title="📣 Cambios en el reino", colour=discord.Colour.gold())
        embed.description = mensaje

        # 7) Adjunta la imagen según la razón
        image_path = get_council_image_path(session.razon)
        if image_path.is_file():
            embed.set_image(url=f"attachment://{image_path.name}")
            await announce_channel.send(
                file=discord.File(image_path, filename=image_path.name),
                embed=embed
            )
        else:
            # Fallback si no existe la imagen
            await announce_channel.send(embed=embed)

    @staticmethod
    def cancel_auto_close(task: asyncio.Task):
        """
        Cancela la tarea de cierre automático si existe.
        """
        if not task.done():
            task.cancel()

    @staticmethod
    def schedule_auto_close(
        session: CouncilSession,
        announce_channel: discord.TextChannel,
        loop: asyncio.AbstractEventLoop,
        delay: Optional[int] = 24 * 3600
    ) -> asyncio.Task:
        """
        Programa el cierre automático y devuelve el Task.
        """
        task = loop.create_task(CouncilService.close_session(session, announce_channel, delay))
        return task
