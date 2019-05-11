import discord
import json
from discord.ext import commands

from bot import Cog

class config(Cog):
    def __init__(self, client):
        self.client = client

    def dump(data):
        with open('config.json', 'w', encoding='utf8') as file:
                json.dump(data, file, indent=4)

    def is_admin():
        async def pred(ctx):
            return ctx.author.id == (ctx.bot.config['bot']['owner_id'] or ctx.guild.owner_id) or ctx.author.guild_permissions.administrator == True
        return commands.check(pred)

    def config_embed(ctx):
        embed = discord.Embed(title='Command: config', description='This command allows you to see and edit the server config.')
        embed.add_field(name='Subcommand: role',
            value='''This subcommand allows you to edit role ID. Usage:
            `config role pending_blurple_light_role [role]`
            `config role pending_blurple_dark_role [role]`
            `config role blurple_light_role [role]`
            `config role blurple_dark_role [role]`
            ''')
        embed.add_field(name='Subcommand: reactionmessage',
            value='''This subcommand allows you to edit the default blurplefier message. Usage:
            `config reactionmessage [message_link]`
            ''')
        embed.add_field(name='Subcommand: show',
            value='''This subcommands shows your current config. Usage:
            `config show`
            ''')
        embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
        embed.color=int(0x7289da)
        return embed

    def guild_config_embed(ctx, data):
        text = '```'
        data = str(data).replace('\'', '').replace('{', '').replace('}', '').replace(',', '\n').replace('\n ', '\n')
        text += data
        text += '```'
        embed = discord.Embed(title='Current server config:', description=text)
        embed.set_footer(text="Blurplefier | " + str(ctx.author), icon_url='https://images-ext-1.discordapp.net/external/2qAD1AHfsqGs7h3CydMrskwnNjHBITIg9atQy9PEIhs/%3Fv%3D1/https/cdn.discordapp.com/emojis/412788702897766401.png')
        embed.color=int(0x7289da)
        return embed


    @is_admin()
    @commands.group(name='config')
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = config.config_embed(ctx)
            return await ctx.send(embed=embed)

    @config.command()
    async def show(self, ctx):
        data = ctx.bot.config['guilds'][str(ctx.guild.id)]
        embed = config.guild_config_embed(ctx, data)
        return await ctx.send(embed=embed)

    @config.command()
    async def role(self, ctx, type: str=None, role: discord.Role=None):
        if type == None:
            return await ctx.send('You need to specify a type.\nExample: `config role blurple_light_role [role]`')
        if role == None:
            return await ctx.send('You need to speciy a role.\nExample: `config role blurple_dark_role DarkTeam`')

        types = ['pending_blurple_light_role', 'pending_blurple_dark_role', 'blurple_dark_role', 'blurple_light_role']
        if not type in types:
            return await ctx.send('Invalid type. Accepted types are: ' + ', '.join(types))

        data = ctx.bot.config
        data['guilds'][str(ctx.guild.id)][type] = role.id
        config.dump(data)
        return await ctx.send('Successfully edited the server config.')

    @config.command()
    async def reactionmessage(self, ctx, message_link: str=None):
        if message_link == None:
            return await ctx.send('You need to specify a message link.\nExample: `config reactionmessage https://discordapp.com/channels/123123123123/456456456456/789789789789`')

        try:
            message_link = message_link.replace(f'https://discordapp.com/channels/{str(ctx.guild.id)}/', '')
            blurplefier_reaction_channel = message_link.split('/')[0]
            blurplefier_reaction_message = message_link.split('/')[1]
        except:
            return await ctx.send('Invalid message link.')

        data = ctx.bot.config
        data['guilds'][str(ctx.guild.id)]['blurplefier_reaction_channel'] = int(blurplefier_reaction_channel)
        data['guilds'][str(ctx.guild.id)]['blurplefier_reaction_message'] = int(blurplefier_reaction_message)
        config.dump(data)
        return await ctx.send('Successfully edited the server config.')

    @Cog.listener()
    async def on_guild_join(self, guild):
        data = self.client.config
        data['guilds'][str(guild.id)] = {
            "pending_blurple_light_role": 0,
            "pending_blurple_dark_role": 0,
            "blurple_light_role": 0,
            "blurple_dark_role": 0,
            "blurplefier_reaction_channel": 0,
            "blurplefier_reaction_message": 0
            }
        config.dump(data)




def setup(bot):
    bot.add_cog(config(bot))
