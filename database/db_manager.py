# database/db_manager.py
from datetime import datetime
import random
from peewee import fn
from .models import (
    JugadorRol,
    db,
    initialize_db,
    Partida,
    Reino,
    Jugador,
    Accion,
)
from config import REIGN_START_PROPS, ROLES, TERRITORIO_TOTAL  # define estos en config.py

def init_db():
    """Inicializa la BD y crea las tablas si no existen."""
    initialize_db()

# ── Partidas ───────────────────────────────────────────────────────────────────

def crear_partida(guild_id: int, nombres_reinos: list[str]) -> Partida:
    """Crea una partida y sus reinos."""
    partida = Partida.create(guild_id=guild_id, nombre=f"Partida {guild_id}")
    for nombre in nombres_reinos:
        Reino.create(
            nombre=nombre,
            partida=partida,
            soldados=REIGN_START_PROPS['soldados'],
            oro=REIGN_START_PROPS['oro'],
            comida=REIGN_START_PROPS['comida'],
            defensa_base=REIGN_START_PROPS['defensa_base'],
            territorio = TERRITORIO_TOTAL // len(nombres_reinos)  # km² de territorio del reino
        )
        
    return partida

def obtener_partida_esperando(guild_id: int) -> Partida | None:
    return (Partida
            .select()
            .where(
                (Partida.guild_id == guild_id) &
                (Partida.estado == 'esperando')
            )
            .first())

def marcar_partida_en_curso(partida: Partida):
    partida.estado = 'en_curso'
    partida.save()

def marcar_partida_finalizada(partida: Partida):
    partida.estado   = 'finalizada'
    partida.fecha_fin = datetime.now()        # ← asignamos un datetime real
    partida.save()

# ── Jugadores ─────────────────────────────────────────────────────────────────

def agregar_jugador_espera(partida: Partida, usuario_id: int, nombre_usuario: str) -> Jugador | None:
    """Agrega un jugador si no existe; si existe devuelve None."""
    existente = (Jugador
                 .select()
                 .where(
                     (Jugador.usuario_id == usuario_id) &
                     (Jugador.partida == partida)
                 )
                 .first())
    if existente:
        return None
    return Jugador.create(
        usuario_id=usuario_id,
        nombre_usuario=nombre_usuario,
        partida=partida
    )

def encontrar_jugador(usuario_id: int) -> Jugador | None:
    return (Jugador.select().where(Jugador.usuario_id == usuario_id).first())

# ── Reparto de reinos y roles ───────────────────────────────────────────────────

def asignar_reinos_y_roles(partida: Partida) -> list[Jugador]:
    """
    1) Reparte N jugadores en M reinos, con N >= M y N <= M*R,
       de modo que ningún reino quede vacío y no se supere R jugadores/reino.
    2) En cada reino asigna cada uno de los R roles a jugadores distintos,
       y reparte los roles sobrantes (R–P_i) al azar entre los P_i miembros.
    """
    reinos    = list(partida.reinos)
    jugadores = list(partida.jugadores)
    random.shuffle(jugadores)

    M = len(reinos)
    R = len(ROLES)
    N = len(jugadores)

    # Validaciones
    if N < M:
        raise ValueError(f"Se necesitan al menos {M} jugadores para cubrir {M} reinos.")
    if N > M * R:
        raise ValueError(f"Demasiados jugadores ({N}); máximo {M*R} para {M} reinos y {R} roles.")

    # ── 1) Asignación de jugadores a reinos ────────────────────────────────────────
    # a) Reservar 1 jugador por reino para que ninguno quede vacío
    realm_map = {}  # Jugador -> Reino
    for i, reino in enumerate(reinos):
        realm_map[jugadores[i]] = reino

    # b) Preparar slots restantes: cada reino tiene R-1 plazas más
    slots_restantes = []
    for reino in reinos:
        slots_restantes += [reino] * (R - 1)

    # c) Asignar los jugadores sobrantes a esos slots al azar
    resto = jugadores[M:]
    muestra = random.sample(slots_restantes, len(resto))
    for jugador, reino in zip(resto, muestra):
        realm_map[jugador] = reino

    # Persistir la asignación de reino
    for jugador, reino in realm_map.items():
        jugador.reino = reino
        jugador.save()

    # ── 2) Asignación de roles por reino ──────────────────────────────────────────
    # Borrar asignaciones anteriores
    JugadorRol.delete().where(JugadorRol.jugador.in_(jugadores)).execute()

    # Para cada reino, cubrir todos los roles sin repetir y repartir sobrantes
    for reino in reinos:
        miembros = [j for j, r in realm_map.items() if r.id == reino.id]
        P = len(miembros)
        if P == 0:
            continue  # (no debería pasar tras la validación)

        # a) Barajar roles y jugadores
        roles_disponibles = ROLES.copy()
        random.shuffle(roles_disponibles)
        random.shuffle(miembros)

        # b) Primera capa: asignar un rol único a cada miembro (P roles de los R)
        asignaciones = {
            miembros[i]: roles_disponibles[i]
            for i in range(P)
        }

        # c) Roles restantes (R – P) se reparten al azar sobre los mismos miembros
        sobrantes = roles_disponibles[P:]
        for rol in sobrantes:
            elegido = random.choice(miembros)
            asignaciones[elegido] += f", {rol}"

        # d) Guardar cada rol en JugadorRol (un registro por rol)
        for jugador, roles_str in asignaciones.items():
            for rol in [r.strip() for r in roles_str.split(",")]:
                JugadorRol.create(jugador=jugador, rol=rol)

    return jugadores

# ── Acciones ──────────────────────────────────────────────────────────────────

def registrar_accion(jugador: Jugador, descripcion: str) -> Accion:
    """Registra una acción del jugador."""
    return Accion.create(jugador=jugador, descripcion=descripcion)
