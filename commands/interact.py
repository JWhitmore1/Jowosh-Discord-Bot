import hikari
import lightbulb
import requests
from db import get_db, check_pair


def interact(ctx, type):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    gif = requests.get('https://usagiapi.danielagc.repl.co/api/'+type).json()['url']

    if type == "hug": color, action = "#50C878", "hugs"
    if type == "kiss": color, action = "#FFB6C1", "kisses"
    if type == "slap": color, action = "#EEDC82", "slaps"
    if type == "bite": color, action = "#FA5F55", "bites"
    if type == "pat": color, action = "#5D3FD3", "pats"

    db = get_db()
    ids = check_pair(sender, recipient, db)
    # what the fuck
    print(ids)
    print(action)
    sent = db.execute('SELECT ? FROM pairs WHERE ID = ?;', (action, ids[0])).fetchone()
    print(sent)
    sent += 1
    db.execute('UPDATE pairs SET ? = ? WHERE ID = ?;', (action, sent, ids[0]))

    embed = hikari.Embed(title=f"You gave a {type}!", color=color)
    embed.add_field(name="** **", value=f"*<@{sender}> {action} <@{recipient}>*")
    if sent == 1:
        embed.set_footer(text=f"That's your first {type} with {ctx.options.user}")
    else:
        embed.set_footer(text=f"That's {sent} {action}!")
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


@lightbulb.option('user', 'Who to bite?', hikari.User)
@lightbulb.command('bite', 'Give this person a bite!')
@lightbulb.implements(lightbulb.SlashCommand)
async def bite(ctx):
    embed = interact(ctx, "bite")
    await ctx.respond(embed)


@lightbulb.option('user', 'Who to pat?', hikari.User)
@lightbulb.command('pat', 'Give this person a pat!')
@lightbulb.implements(lightbulb.SlashCommand)
async def pat(ctx):
    embed = interact(ctx, "pat")
    await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.command(hug)
    bot.command(kiss)
    bot.command(slap)
    bot.command(bite)
    bot.command(pat)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("hug"))
    bot.remove_command(bot.get_slash_command("kiss"))
    bot.remove_command(bot.get_slash_command("slap"))
    bot.remove_command(bot.get_slash_command("bite"))
    bot.remove_command(bot.get_slash_command("pat"))
