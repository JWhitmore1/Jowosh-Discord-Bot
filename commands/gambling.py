import lightbulb
import random

f = open('options.txt', 'r')
#   thanks to @sponkle#6445 for the options
options_8ball = f.read().split('\n')
# print(options_8ball)

gambling_plugin = lightbulb.Plugin("Gambling")

@lightbulb.plugin()
@lightbulb.option('question', 'Ask away', type=str)
@lightbulb.command('8ball', 'What will the ball decide!?!?')
@lightbulb.implements(lightbulb.SlashCommand)
async def ball(ctx):
    await ctx.respond(ctx.options.question + '\n :8ball:  |  ' + random.choice(options_8ball))


@lightbulb.plugin()
@lightbulb.command('coinflip', 'do you get head or tail!?')
@lightbulb.implements(lightbulb.SlashCommand)
async def flip(ctx):
    result = random.randint(0, 1)
    if result == 1:
        await ctx.respond(":coin: | You flipped Heads!")
    else:
        await ctx.respond(":coin: | You flipped Tails!")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(gambling_plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(gambling_plugin)

