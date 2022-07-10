import hikari
import lightbulb
import random
from db import get_db, check_pair

f = open('kill.txt', 'r')
kill_options = f.read().split('\n')


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
    bot.command(kill)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("kill"))
