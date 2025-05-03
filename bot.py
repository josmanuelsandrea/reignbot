import discord
from discord.ext import commands
from config import TOKEN
from database.models import initialize_db
from utils.cogs_loader import load_cogs

class MyBot(commands.Bot):
    def __init__(self):
        # 1) Define los intents y habilita el privileged intent de miembros
        intents = discord.Intents.default()
        intents.members = True

        # 2) Pásalos al super() para que el bot se construya con ellos
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # Ya NO creas otro Bot aquí, usas self
        initialize_db()  
        await load_cogs(self, directory="cogs")
        await self.tree.sync()

if __name__ == "__main__":
    bot = MyBot()
    bot.run(TOKEN)
