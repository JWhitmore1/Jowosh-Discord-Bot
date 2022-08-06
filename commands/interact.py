import hikari
import lightbulb
import requests
import random
from db import get_db, check_pair

f = open('kill.txt', 'r')
kill_options = f.read().split('\n')

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
    sent = db.execute(f"SELECT {action} FROM pairs WHERE ID = ?;", (ids[0],)).fetchone()[0]
    sent += 1
    db.execute(f'UPDATE pairs SET {action} = ? WHERE ID = ?;', (sent, ids[0]))
    db.commit()

    embed = hikari.Embed(title=f"You gave a {type}!", color=color)
    embed.add_field(name="** **", value=f"*<@{sender}> {action} <@{recipient}>*")
    if sent == 1:
        embed.set_footer(text=f"That's your first {type} with {ctx.options.user}")
    else:
        embed.set_footer(text=f"That's {sent} {action}!")
    embed.set_image(gif)
    return embed

plugin = lightbulb.Plugin("Interact")


@plugin.command()
@lightbulb.option('user', 'Who to hug?', hikari.User)
@lightbulb.command('hug', 'Give this person a big hug!')
@lightbulb.implements(lightbulb.SlashCommand)
async def hug(ctx):
    embed = interact(ctx, "hug")
    await ctx.respond(embed)


@plugin.command()
@lightbulb.option('user', 'Who to kiss?', hikari.User)
@lightbulb.command('kiss', 'Give this person a passionate kiss!')
@lightbulb.implements(lightbulb.SlashCommand)
async def kiss(ctx):
    embed = interact(ctx, "kiss")
    await ctx.respond(embed)


@plugin.command()
@lightbulb.option('user', 'Who to slap?', hikari.User)
@lightbulb.command('slap', 'Give this person a slap!')
@lightbulb.implements(lightbulb.SlashCommand)
async def slap(ctx):
    embed = interact(ctx, "slap")
    await ctx.respond(embed)


@plugin.command()
@lightbulb.option('user', 'Who to bite?', hikari.User)
@lightbulb.command('bite', 'Give this person a bite!')
@lightbulb.implements(lightbulb.SlashCommand)
async def bite(ctx):
    embed = interact(ctx, "bite")
    await ctx.respond(embed)


@plugin.command()
@lightbulb.option('user', 'Who to pat?', hikari.User)
@lightbulb.command('pat', 'Give this person a pat!')
@lightbulb.implements(lightbulb.SlashCommand)
async def pat(ctx):
    embed = interact(ctx, "pat")
    await ctx.respond(embed)


@plugin.command
@lightbulb.option('user', 'who to kill', hikari.User)
@lightbulb.command('kill', 'kill.')
@lightbulb.implements(lightbulb.SlashCommand)
async def kill(ctx):
    sender = str(ctx.member.id)
    recipient = str(ctx.options.user.id)
    if sender == recipient:
        await ctx.respond("~noooooo dont kill urslef u r so hot and secsy :weary:")
    else:
        db = get_db()
        ids = check_pair(sender, recipient, db)

        kills = db.execute('SELECT kills FROM pairs WHERE ID = ?;', (ids[0],)).fetchone()[0]
        deaths = db.execute('SELECT kills FROM pairs WHERE ID = ?;', (ids[1],)).fetchone()[0]

        kills += 1

        db.execute('UPDATE pairs SET kills = ? WHERE ID = ?;', (kills, ids[0]))

        db.commit()

        embed = hikari.Embed(title=f"{random.choice(kill_options)}", color="#DC143C")
        embed.add_field(name="\u200b", value=f"*<@{sender}> killed <@{recipient}>*", inline=True)
        embed.set_footer(text=f"{kills} vs. {deaths}")
        await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
