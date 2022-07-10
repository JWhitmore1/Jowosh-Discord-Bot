from tkinter import font
import hikari
import lightbulb
import random
import requests
from dotenv import load_dotenv
import os

f = open('options.txt', 'r')
#   thanks to @sponkle#6445 for the options
options_8ball = f.read().split('\n')
# print(options_8ball)

load_dotenv()
bot = lightbulb.BotApp(
    token=os.environ.get("bot_token"), 
    default_enabled_guilds=(853171732319174667)
    )

# @bot.listen(hikari.StartedEvent)
# async def bot_started(event):
#     await bot.presences.activity("with peoples feelings")

@bot.listen(hikari.GuildMessageCreateEvent)
async def print_message(event):
    # print(event.content)
    if event.is_bot or not event.content:
        return

    if event.content.startswith("hi jowosh"):
        await event.message.respond("Hello!! ^-^")

@bot.command
@lightbulb.option('question', 'Ask away', type=str)
@lightbulb.command('8ball', 'What will the ball decide!?!?')
@lightbulb.implements(lightbulb.SlashCommand)
async def ball(ctx):
    await ctx.respond(ctx.options.question + '\n :8ball:  |  ' + random.choice(options_8ball))
    
@bot.command
@lightbulb.command('inspire', 'Generates inspirational quote')
@lightbulb.implements(lightbulb.SlashCommand)
async def inspire(ctx):
    r = requests.get('https://inspirobot.me/api?generate=true')
    link = r.content.decode('utf-8')
    await ctx.respond(link)

@bot.command
@lightbulb.command('test', 'test embed')
@lightbulb.implements(lightbulb.SlashCommand)
async def test(ctx):
    embed = hikari.Embed(title="title")
    await ctx.respond(embed)

@bot.command
@lightbulb.option('text', 'What will Jowosh say', type=str)
# @lightbulb.option('channel', 'channel for jowosh to speak into', type=channel)
@lightbulb.command('say', 'Speak vicariously through Jowosh')
@lightbulb.implements(lightbulb.SlashCommand)
async def say(ctx):
    channel = ctx.get_channel()
    await channel.send(ctx.options.text)
    await ctx.respond('** **', delete_after=0)

@bot.command
@lightbulb.option('text', 'What will Jowosh say', type=str)
@lightbulb.command('banner', 'Speak through Jowosh, clearly!')
@lightbulb.implements(lightbulb.SlashCommand)
async def banner(ctx):
    message = ''
    conv = {'0': 'zero',
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine'}

    for char in ctx.options.text:
        if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            message += f':regional_indicator_{char.lower()}: '
        elif char in '0123456789':
            num = conv[char]
            message += f':{num}: '
        elif char == ' ':
            message += '   '
        else:
            message += char

    await ctx.respond(message)

@bot.command
@lightbulb.option('user', 'Who to hug?', hikari.User)
@lightbulb.command('hug', 'Give this person a big hug!')
@lightbulb.implements(lightbulb.SlashCommand)
async def hug(ctx): 
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    embed = hikari.Embed(title = "You gave a hug!", color="#50C878")
    embed.add_field(name = "** **", value = "*<@"+sender+"> hugs "+"<@"+recipient+">*")
    await ctx.respond(embed)

@bot.command
@lightbulb.option('user', 'Who to kiss?', hikari.User)
@lightbulb.command('kiss', 'Give this person a passionate kiss!')
@lightbulb.implements(lightbulb.SlashCommand)
async def kiss(ctx):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    embed = hikari.Embed(title = "You gave a kiss!", color="#FFB6C1")
    embed.add_field(name = "** **", value = "*<@"+sender+"> kisses "+"<@"+recipient+">*")
    await ctx.respond(embed)

@bot.command
@lightbulb.option('user', 'Who to slap?', hikari.User)
@lightbulb.command('slap', 'Give this person a slap!')
@lightbulb.implements(lightbulb.SlashCommand)
async def slap(ctx):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    embed = hikari.Embed(title = "You gave a slap!", color="#EEDC82")
    embed.add_field(name = "** **", value = "*<@"+sender+"> slaps "+"<@"+recipient+">... ouch!*")
    await ctx.respond(embed)

bot.run()