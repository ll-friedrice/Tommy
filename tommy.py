
# **************************************** #
# tommy.py
# Written by x2110311x
# Main file for running Tommy
# **************************************** #

# Include Libraries #
import asyncio
import discord
import logging
import time
import yaml

from difflib import SequenceMatcher
from datetime import datetime
from discord.ext import commands
from include import utilities, DB
from os import system
from os.path import abspath


# General Variables #
with open(abspath('./config/config.yml'), 'r') as configFile:
    config = yaml.safe_load(configFile)

bot = commands.Bot(command_prefix=config['commandPrefix'])

DBConn = None

load_errors = []
for extension in config['enabled_extensions']:  
    try:
        extension = f"cogs.{extension}"
        bot.load_extension(extension)
    except:
        load_errors.append(f"Unable to load {extension}")

@bot.listen()
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = ctx.message.content[1:]
        cmdIndex = message.find(" ")
        if cmdIndex != -1:
            usedCommand = message[:cmdIndex]
        else:
            usedCommand = message
        foundCommand = None
        highestRatio = 0.0
        for command in bot.commands:
            commandName = command.name
            comparison = SequenceMatcher(None, usedCommand, commandName)
            if comparison.ratio() > highestRatio:
                highestRatio = comparison.ratio()
                foundCommand = command
        await ctx.send(f"Hmm! You forgot to specify {error.param}\n ```Usage: !{foundCommand.name} {foundCommand.usage}```")
    elif isinstance(error, commands.ExtensionNotLoaded):
        await ctx.send(f"Uhoh! The {error.name} extension is not loaded! Please contact x2110311x")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("You can't use commands in DMs!")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        message = ctx.message.content[1:]
        cmdIndex = message.find(" ")
        if cmdIndex != -1:
            usedCommand = message[:cmdIndex]
        else:
            usedCommand = message
        foundCommand = None
        highestRatio = 0.0
        for command in bot.commands:
            commandName = command.name
            comparison = SequenceMatcher(None, usedCommand, commandName)
            if comparison.ratio() > highestRatio:
                highestRatio = comparison.ratio()
                foundCommand = command
        if foundCommand is not None:
            embedUnknownCommand = discord.Embed(title=f"Unknown command: !{usedCommand}", colour=0x753543)
            embedUnknownCommand.add_field(
                name=f"Did you mean to use !{foundCommand.name}?", value=foundCommand.brief, inline=False)
            if foundCommand.usage is None:
                cmdUsage = ""
            else:
                cmdUsage = foundCommand.usage
            embedUnknownCommand.add_field(
                name="Usage", value=f"!{foundCommand.name} {cmdUsage}", inline=False)
            await ctx.send(embed=embedUnknownCommand)
    else:
        await ctx.send(f"Unknown error occured. Please contact x2110311x \n{error}")


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@bot.listen()
async def on_ready():
    print("Logged in")

    global DBConn
    DBConn = await DB.connect()

    # Message Testing Channel #
    chanTest = bot.get_channel(config['testing_Channel'])
    await chanTest.send("Bot has started")
    for error in load_errors:
        await chanTest.send(error)

    # Update Status #
    guild = bot.get_guild(config['server_ID'])
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"with {guild.member_count - config['botCount']} members"))


bot.run(config['token'], bot=True, reconnect=True)
