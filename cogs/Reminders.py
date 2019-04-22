import sqlite3
import time
import yaml

from datetime import datetime
from discord.ext import commands
from os.path import abspath

# General Variables #
with open(abspath('./include/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

with open(abspath(config['help_file']), 'r') as helpFile:
    helpInfo = yaml.safe_load(helpFile)

helpInfo = helpInfo['Reminders']

# Database connections #
DBConn = sqlite3.connect(abspath(config['DBFile']))
DB = DBConn.cursor()


class SaidNoError(Exception):
    pass


class Reminders(commands.Cog, name="Reminder Commands"):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(brief=helpInfo['remind']['brief'], usage=helpInfo['remind']['usage'])
    async def remind(self, ctx, remindTime, *, remindReason):
        try:
            remindEpoch = int(time.time()) + (int(remindTime) * 60)
            author = ctx.message.author
            remindInsert = f"INSERT INTO Reminders (User, Reminder, Date) VALUES ({author.id},'{remindReason}',{remindEpoch})"
            DB.execute(remindInsert)
            DBConn.commit()
            await ctx.send(f"You will be reminded in {remindTime} minutes for `{remindReason}`")
        except ValueError:
            await ctx.send("Please do not use decimals")

    @commands.command(brief=helpInfo['myreminders']['brief'], usage=helpInfo['myreminders']['usage'], alias="myreminds")
    async def myreminders(self, ctx):
        author = ctx.message.author
        remindSelect = f"SELECT Reminder, Date FROM Reminders WHERE User = {author.id}"
        DB.execute(remindSelect)
        reminds = DB.fetchall()
        if len(reminds) > 0:
            remindString = "Your reminders: \n```\n"
            for remind in reminds:
                reason = remind[0]
                date = datetime.fromtimestamp(remind[1]).strftime("%m/%d/%Y, %H:%M:%S") + " EST"
                remindString += f"{reason}  at {date} \n"
            remindString += "```"
            await ctx.send(remindString)
        else:
            await ctx.send("You have no reminders")


def setup(bot):
    bot.add_cog(Reminders(bot))


def teardown(bot):
    DB.close()