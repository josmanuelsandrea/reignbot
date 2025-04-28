from dataclasses import dataclass, field
from typing import List

@dataclass
class Reino:
    nombre: str
    territorio: int
    soldados: int
    oro: int
    moral: int
    alimentacion: int
    defensa_base: int
    jugadores: List[int] = field(default_factory=list)
