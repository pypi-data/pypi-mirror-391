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
    @qr_commands.slash_command(name="migrate", description="Migration Response")
    async def migrate(self, ctx):
        await ctx.trigger_typing()

        if ctx.guild:
            embd = Embed(description="We have begun the process of decommissioning SeAT and have begun the migration to Alliance Auth. \n\n**You will need to log into here:**\nhttps://auth.black-rose.space\n\n**The Activate CharLink here:**\nhttps://auth.black-rose.space/charlink/\n\n**Then Activate the Discord Service here:**\nhttps://auth.black-rose.space/services/\n\n**Then apply for groups in here:**\nhttps://auth.black-rose.space/groups/\n\nIf you still need assistance please use:\n```\n/help\n```",
                      colour=0x00b0f4)

            embd.set_author(name="SeAT to Auth Migration!")

            return await ctx.respond(embed=embd)


def setup(bot):
    unload_cog(bot=bot, cog_name="qr")
    bot.add_cog(qr(bot))