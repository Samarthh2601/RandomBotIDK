import asyncio
import hikari
import lightbulb

from ..core import Yuuki
from ..utils import COLOURS

class Misc(lightbulb.Plugin):
    def __init__(self):
        super().__init__("Miscellanous commands!", "Miscellaneous Utility commands@")
        
misc = Misc()


@misc.command
@lightbulb.command(name="ping", description="Get my ping in milliseconds!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(description=f"My Ping is **{round(misc.bot.heartbeat_latency * 1000)}**ms!")
    await ctx.respond(embed=embed)

@misc.command
@lightbulb.command(name="uptime", description="Get my uptime!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def uptime(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(f"My Uptime -> `{misc.bot.uptime}`")

def load(bot: Yuuki):
    bot.add_plugin(misc)