import hikari
import lightbulb
import random

f = open('kill.txt', 'r')
#   thanks to @sponkle#6445 for the options
kill_options = f.read().split('\n')
# print(options_8ball)


@lightbulb.option('user', 'who to kill', hikari.User)
@lightbulb.command('kill', 'kill.')
@lightbulb.implements(lightbulb.SlashCommand)
async def kill(ctx):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)

    embed = hikari.Embed(title=f"{random.choice(kill_options)}", color="#DC143C")
    embed.add_field(name="** **", value=f"*<@{sender}> killed <@{recipient}>*")
    await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.command(kill)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("kill"))
