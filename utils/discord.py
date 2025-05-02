import discord
from discord.utils import get

async def get_or_create_role(guild: discord.Guild, name: str) -> discord.Role:
    role = get(guild.roles, name=name)
    if not role:
        role = await guild.create_role(name=name)
    return role
