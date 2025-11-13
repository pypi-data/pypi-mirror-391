import logging

from discord.colour import Color
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

from aadiscordbot import __branch__, __version__
from aadiscordbot.app_settings import get_site_url

from adieu_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)

class qr(commands.Cog):

    """
    Custom Quick Replies for discord
    """

    def __init__(self, bot):
    self.bot = bot
    
    qr_commands = SlashCommandGroup("qr", "A Collection of Quick Response bot commands")
    @qr_commands.command(name="migrate", description="Migration Response")
    async def discordbot(self, ctx):
        await ctx.trigger_typing()

        embd = Embed(title="AllianceAuth")
        embd.set_thumbnail(
            url="https://assets.gitlab-static.net/uploads/-/system/project/avatar/6840712/Alliance_auth.png?width=128"
        )
        embd.colour = Color.blue()

        embd.description = "All Authentication functions for this Discord server are handled through our Alliance Auth install"

        url = get_site_url()

        embd.add_field(
            name="Auth Link", value=url, inline=False
        )

        return await ctx.send(embed=embd)


def setup(bot):
    unload_cog(bot=bot, cog_name="qr")
    bot.add_cog(qr(bot))