import lightbulb
import random

f = open('options.txt', 'r')
#   thanks to @sponkle#6445 for the options
options_8ball = f.read().split('\n')
# print(options_8ball)


@lightbulb.option('question', 'Ask away', type=str)
@lightbulb.command('8ball', 'What will the ball decide!?!?')
@lightbulb.implements(lightbulb.SlashCommand)
async def ball(ctx):
    await ctx.respond(ctx.options.question + '\n :8ball:  |  ' + random.choice(options_8ball))


def load(bot: lightbulb.BotApp):
    bot.command(ball)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("ball"))
