import discord
import os
import yaml
import random

from datetime import datetime
from discord.ext import commands
from discord.utils import get
from discord.ext.commands.errors import CommandNotFound, CommandInvokeError
from dotenv import load_dotenv
from os import system

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = "!"

bot = commands.Bot(command_prefix=BOT_PREFIX)


def commands_dict():
    with open("commands.yaml", encoding="utf8") as infile:
        commands_dict = yaml.safe_load(infile)
    return commands_dict


# delete from current chat the last <amount> + 1 messages(command included)
async def clr(ctx, amount=0):
    if ctx.author == bot.user:
        return
    await ctx.channel.purge(limit=amount + 1)


# send dick pic
async def send_callback(ctx):
    if ctx.author == bot.user:
        return
    await ctx.channel.send(commands_dict[ctx.command.qualified_name]["text"])


# send random butthole
async def random_send_callback(ctx):
    if ctx.author == bot.user:
        return
    await ctx.channel.send(
        random.choice(commands_dict[ctx.command.qualified_name]["choices"])
    )


# play shit
async def audio_callback(ctx):
    if ctx.message.author.voice == None:
        return
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(
            f"{datetime.now().strftime('%H:%M:%S')} The bot has connected to {channel} "
            f"[requested by {ctx.author.name} ({ctx.author})]"
        )
    voice = get(bot.voice_clients, guild=ctx.guild)

    voice.play(
        discord.FFmpegPCMAudio(commands_dict[ctx.command.qualified_name]["file"]),
        after=lambda e: print(
            f"{datetime.now().strftime('%H:%M:%S')} Finished playing !{ctx.command.qualified_name}"
        ),
    )
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.65
    while voice.is_playing() == True:
        continue
    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"{datetime.now().strftime('%H:%M:%S')} The bot has left {channel}\n")
    if ctx.author == bot.user:
        return


# build all commands from dict
def command_builder(commands_dict):
    command_list = []
    for command_name in commands_dict:
        if commands_dict[command_name]["type"] == "send":
            func = send_callback
        elif commands_dict[command_name]["type"] == "audio":
            func = audio_callback
        elif commands_dict[command_name]["type"] == "random_choice":
            func = random_send_callback
        else:
            continue
        c = commands.Command(
            func, name=command_name, help=commands_dict[command_name]["help"]
        )
        command_list.append(c)
    return command_list


# display when the bot is connected to discord
@bot.event
async def on_ready():
    print(
        f"{datetime.now().strftime('%H:%M:%S')} {bot.user.name} has connected to Discord!"
    )


# prevent CLI spam from non-existent commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (CommandInvokeError, CommandNotFound)):
        return
    raise error


if __name__ == "__main__":
    commands_dict = commands_dict()
    commands = command_builder(commands_dict)
    for c in commands:
        bot.add_command(c)
    bot.run(TOKEN)
