import os
from pathlib import Path


def get_image_folder() -> Path:
    """
    Devuelve la ruta absoluta de la carpeta donde se almacenan las imágenes de resultados del consejo.
    """
    # __file__ apunta a utils/path_utils.py
    # Asumimos la siguiente estructura de proyecto:
    # project_root/
    # ├─ utils/
    # │  └─ path_utils.py
    # ├─ cogs/
    # ├─ services/
    # └─ images/resultados/
    base_dir = Path(__file__).resolve().parent.parent  # project_root
    return base_dir / 'assets' / 'consejo'


def get_council_image_path(reason_key: str, extension: str = 'png') -> Path:
    """
    Construye la ruta absoluta de la imagen para la razón de consejo dada.

    :param reason_key: Clave de la razón en COUNCIL_REASONS (ej. 'renombrar').
    :param extension: Extensión de la imagen (por defecto 'png').
    :return: Path absoluto al fichero de imagen.
    """
    folder = get_image_folder()
    filename = f"{reason_key}.{extension}"
    return folder / filename
