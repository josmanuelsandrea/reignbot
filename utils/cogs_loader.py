# cogs_loader.py
"""
Utilería para cargar automáticamente todos los cogs (extensiones) de la carpeta `cogs/` y sus subdirectorios.
"""
import os
from discord.ext import commands

async def load_cogs(bot: commands.Bot, directory: str = "cogs"):
    """
    Carga recursivamente todas las extensiones (.py) dentro de `directory`.

    Parámetros:
    - bot: instancia de commands.Bot donde registrar las extensiones.
    - directory: ruta al directorio raíz de cogs (por defecto "cogs").

    Ignora archivos que:
    - No terminen en .py
    - Empiecen por "__"
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            # Filtrar solo .py y evitar __init__.py o privados
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            # Construir el path de módulo (e.g., cogs.partida.crear)
            rel_dir = os.path.relpath(root, ".").replace(os.sep, ".")
            module_name = f"{rel_dir}.{filename[:-3]}"

            try:
                await bot.load_extension(module_name)
                print(f"Cargado {module_name}")
            except Exception as e:
                print(f"Error al cargar {module_name}: {e}")

# Ejemplo de uso en bot.py:
#
# Supongamos que tienes tu cargador en `utils/cogs_loader.py` y tus Cogs en la carpeta `cogs/`.
# Así integras `load_cogs` dentro de tu clase MyBot:
#
# import discord
# from discord.ext import commands
# from config import TOKEN
# from database.db_manager import inicializar_db
# from utils.cogs_loader import load_cogs
#
# class MyBot(commands.Bot):
#     def __init__(self):
#         super().__init__(
#             command_prefix="!",
#             intents=discord.Intents.default()
#         )
#
#     async def setup_hook(self):
#         # 1. Inicializas la base de datos
#         inicializar_db()
#         # 2. Cargas todos los cogs de 'cogs/' recursivamente
#         await load_cogs(self, directory="cogs")
#         # 3. Sincronizas tus slash commands
#         await self.tree.sync()
#
# if __name__ == "__main__":
#     bot = MyBot()
#     bot.run(TOKEN)
