import discord
from discord.ext import commands

from bot import Cog

class help(Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='help')
    async def help_command(self, ctx, command=''):
        def default_embed():
            embed = discord.Embed(title='help', description='Lists commands or provides advanced help for a command.\n`help <command>`')
            embed.color=int(0x7289da)
            embed.add_field(name='blurplefy', value='Manipulate the image color over a curve of your three team colors.')
            embed.add_field(name='check', value='Check an image to get the Blurple User role.')
            embed.add_field(name='lightfy', value='Manipulate the image color over a curve of dark blurple, blurple, and white.')
            embed.add_field(name='darkfy', value='Manipulate the image color over a curve of not quite black, dark blurple, and blurple.')
            embed.add_field(name='rollteam', value='Gives you a pending team role.')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def help_embed():
            embed = discord.Embed(title='Command: help', description='Lists commands or provides help for a command.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`help <command>`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def blurplefy_embed():
            embed = discord.Embed(title='Command: blurplefy', description='Manipulate the image color over a curve of your three team colors.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`blurplefy [method] [variations=[None]]... [who]`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def check_embed():
            embed = discord.Embed(title='Command: check', description='Check an image to get the Blurple User role.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`check [who]`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def lightfy_embed():
            embed = discord.Embed(title='Command: lightfy', description='Manipulate the image color over a curve of dark blurple, blurple, and white.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`lightfy [method] [variations=[None]]... [who]`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def darkfy_embed():
            embed = discord.Embed(title='Command: darkfy', description='Manipulate the image color over a curve of not quite black, dark blurple, and blurple.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`darkfy [method] [variations=[None]]... [who]`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def error_embed():
            embed = discord.Embed(title='Command not found', description='Please re-check your help query.')
            embed.color = int(0x7289da)
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        def rollteam_embed():
            embed = discord.Embed(title='Command: rollteam', description='Gives you a pending team role.')
            embed.color = int(0x7289da)
            embed.add_field(name='Usage:', value='`rollteam`')
            embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
            return embed

        HELP_MESSAGES = {
            '' : default_embed(),
            'help' : help_embed(),
            'blurplefy' : blurplefy_embed(),
            'check' : check_embed(),
            'lightfy' : lightfy_embed(),
            'darkfy' : darkfy_embed(),
            'error' : error_embed(),
            'rollteam': rollteam_embed()
        }

        try:
            message = HELP_MESSAGES[command]
        except KeyError:
            message = HELP_MESSAGES['error']

        await ctx.send(embed=message)



def setup(bot):
    bot.remove_command('help')
    bot.add_cog(help(bot))
