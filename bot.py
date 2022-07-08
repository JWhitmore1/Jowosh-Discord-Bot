import hikari
import lightbulb
import random
from dotenv import load_dotenv
import os


options_8ball = [
    # thanks to @sponkle#6445 for the options
    'Certainly not.', 
    'Absolutely!', 
    'It is certain.',
    'It is reasonably sure.',
    'There are some slight doubts.', 
    'No. Never. Stop. Now.', 
    'Ballsn\'t', 
    'Bruh? u fr rn?',
    'Naur :skull:',
]

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
async def ping(ctx):
    await ctx.respond(ctx.options.question + '\n\n :8ball:  |  ' + random.choice(options_8ball))
    
bot.run()

