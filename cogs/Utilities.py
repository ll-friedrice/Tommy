import discord
import time
import yaml

from datetime import datetime
from discord.ext import commands
from include import utilities, DB
from os import system
from os.path import abspath


with open(abspath('./config/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

with open(abspath(config['info_file']), 'r') as info_file:
    info = yaml.safe_load(info_file)

helpInfo = helpInfo['Utilities']
intStartTime = int(time.time())  # time the bot started at

async def is_owner(ctx):
    return ctx.author.id == int(config['owner'])


class Utilities(commands.Cog, name="Utility Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['epoch']['brief'], usage=helpInfo['epoch']['usage'])
    async def epoch(self, ctx):
        intCurEpoch = int(time.time())
        await ctx.send(f"The current epoch is {intCurEpoch}")

    @commands.command(brief=helpInfo['fromepoch']['brief'], usage=helpInfo['fromepoch']['usage'])
    async def fromepoch(self, ctx, epoch: int):
        dateTime = datetime.utcfromtimestamp(epoch).strftime("%m/%d/%Y, %H:%M:%S") + " GMT"
        await ctx.send(f"{epoch} is {dateTime}")

    @commands.command(brief=helpInfo['reloadextensions']['brief'], usage=helpInfo['reloadextensions']['usage'])
    @commands.check(is_owner)
    async def reloadextensions(self, ctx):
        load_errors = []
        for extension in config['enabled_extensions']:  
            try:
                extension = f"cogs.{extension}"
                bot.reload_extension(extension)
            except:
                load_errors.append(f"Unable to load {extension}")
            finally:
                await ctx.send("Extensions reloaded!")

    @commands.command(brief=helpInfo['update']['brief'], usage=helpInfo['update']['usage'])
    @commands.check(is_owner)
    async def update(self, ctx):
        await ctx.send("Updating Bot")
        updateScript = abspath(config['update_script'])
        system(f'sudo {updateScript}')

    @commands.command(brief=helpInfo['update']['brief'], usage=helpInfo['update']['usage'])
    @commands.check(is_owner)
    async def restart(self, ctx):
        await ctx.send("Restarting Bot")
        restart_script = abspath(config['restart_script'])
        system(f'sudo {restart_script}')

    @commands.command(brief=helpInfo['ping']['brief'], usage=helpInfo['ping']['usage'])
    async def ping(self, ctx):
        msgResp = await ctx.send("Bot is up!")
        editStamp = utilities.msdiff(ctx.message.created_at, msgResp.created_at)
        strResp = f"Pong! `{editStamp}ms`"
        await msgResp.edit(content=strResp)

    @commands.command(brief=helpInfo['uptime']['brief'], usage=helpInfo['uptime']['usage'])
    async def uptime(self, ctx):
        nowtime = time.time()
        uptime = utilities.seconds_to_units(int(nowtime - intStartTime))
        await ctx.send(f"{info['name']} has been online for `{uptime}`.")

def setup(bot):
    bot.add_cog(Utilities(bot))