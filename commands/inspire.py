import lightbulb
import requests


@lightbulb.command('inspire', 'Generates inspirational quote')
@lightbulb.implements(lightbulb.SlashCommand)
async def inspire(ctx):
    r = requests.get('https://inspirobot.me/api?generate=true')
    link = r.content.decode('utf-8')
    await ctx.respond(link)


def load(bot: lightbulb.BotApp):
    bot.command(inspire)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("inspire"))