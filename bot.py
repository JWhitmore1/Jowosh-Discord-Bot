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
@lightbulb.command('say', 'Speak vicariously through Jowosh')
@lightbulb.implements(lightbulb.SlashCommand)
async def say(ctx):
    await ctx.respond(ctx.options.text)

@bot.command
@lightbulb.option('text', 'What will Jowosh say', type=str)
@lightbulb.command('banner', 'Speak through Jowosh, clearly!')
@lightbulb.implements(lightbulb.SlashCommand)
async def say(ctx):
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

bot.run()

