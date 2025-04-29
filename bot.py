import discord
from discord.ext import commands
from config import TOKEN
from database.db_manager import inicializar_db

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default()
        )

    async def setup_hook(self):
        # Carga la extensión donde está tu Cog
        inicializar_db()  # Inicializa la base de datos
        await self.load_extension("cogs.actions.diplomatic_actions")
        await self.load_extension("cogs.manage_game")
        # Sincroniza los slash commands (globales)
        await self.tree.sync()

if __name__ == "__main__":
    bot = MyBot()
    bot.run(TOKEN)
