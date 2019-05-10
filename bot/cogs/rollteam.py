import discord
import random
from discord.ext import commands

from bot import Cog

class rollteam(Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='rollteam')
    async def rollteam_command(self, ctx, command=''):
        dark = ctx.bot.config['guilds'][str(ctx.guild.id)]['pending_blurple_dark_role']
        light = ctx.bot.config['guilds'][str(ctx.guild.id)]['pending_blurple_light_role']
        dark = ctx.guild.get_role(dark)
        light = ctx.guild.get_role(light)
        try:
            await ctx.author.remove_roles(dark)
        except:
            pass
        try:
            await ctx.author.remove_roles(light)
        except:
            pass
        await ctx.author.add_roles(random.choice([dark, light]))
        await ctx.send('Successfully assigned you to a team!')



def setup(bot):
    bot.add_cog(rollteam(bot))
