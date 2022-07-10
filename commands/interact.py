import hikari
import lightbulb
import requests


def interact(ctx, type):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    gif = requests.get('https://usagiapi.danielagc.repl.co/api/'+type).json()['url']

    if type == "hug": color, action = "#50C878", "hugs"
    if type == "kiss": color, action = "#FFB6C1", "kisses"
    if type == "slap": color, action = "#EEDC82", "slaps"

    embed = hikari.Embed(title=f"You gave a {type}!", color=color)
    embed.add_field(name="** **", value=f"*<@{sender}> {action} <@{recipient}>*")
    embed.set_image(gif)
    return embed


@lightbulb.option('user', 'Who to hug?', hikari.User)
@lightbulb.command('hug', 'Give this person a big hug!')
@lightbulb.implements(lightbulb.SlashCommand)
async def hug(ctx):
    embed = interact(ctx, "hug")
    await ctx.respond(embed)


@lightbulb.option('user', 'Who to kiss?', hikari.User)
@lightbulb.command('kiss', 'Give this person a passionate kiss!')
@lightbulb.implements(lightbulb.SlashCommand)
async def kiss(ctx):
    embed = interact(ctx, "kiss")
    await ctx.respond(embed)


@lightbulb.option('user', 'Who to slap?', hikari.User)
@lightbulb.command('slap', 'Give this person a slap!')
@lightbulb.implements(lightbulb.SlashCommand)
async def slap(ctx):
    embed = interact(ctx, "slap")
    await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.command(hug)
    bot.command(kiss)
    bot.command(slap)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("hug"))
    bot.remove_command(bot.get_slash_command("kiss"))
    bot.remove_command(bot.get_slash_command("slap"))
