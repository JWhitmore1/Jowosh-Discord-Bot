import lightbulb
import hikari

plugin = lightbulb.Plugin("Communication")


@plugin.command()
@lightbulb.command('guydisintegratinggif', 'just a guy disintegrating dw bout it')
@lightbulb.implements(lightbulb.SlashCommand)
async def disintegrate(ctx):
    await ctx.respond(hikari.File("./static/gif/guydisintegratinggif.gif"))


@plugin.command()
@lightbulb.option('text', 'What will Jowosh say', type=str)
@lightbulb.command('say', 'Speak vicariously through Jowosh')
@lightbulb.implements(lightbulb.SlashCommand)
async def say(ctx):
    channel = ctx.get_channel()
    await channel.send(ctx.options.text)
    await ctx.respond('** **', delete_after=0)


@plugin.command()
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


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)