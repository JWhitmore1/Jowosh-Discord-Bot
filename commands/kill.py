import hikari
import lightbulb
import random
from db import get_db, id_exists

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
        pair_id = sender + recipient
        # print("\n\n" + pair_id)
        reverse = recipient + sender

        db = get_db()

        if id_exists(reverse, db):
            # print('reverse exists')
            data = db.execute('SELECT kills, killeds FROM pairs WHERE ID = ?;', (reverse,)).fetchone()
            kills = data[1] + 1
            killeds = data[0]
            db.execute('UPDATE pairs SET killeds = ? WHERE ID = ?;', (kills, reverse))
        else:
            if not id_exists(pair_id, db):
                # print('pair doesn\'t exist')
                db.execute('INSERT INTO pairs (ID) VALUES (?);', (pair_id,))
            else:
                # print('pair exists')
                pass

            data = db.execute('SELECT kills, killeds FROM pairs WHERE ID = ?;', (pair_id,)).fetchone()
            kills = data[0] + 1
            killeds = data[1]
            db.execute('UPDATE pairs SET kills = ? WHERE ID = ?;', (kills, pair_id))

        db.commit()

        embed = hikari.Embed(title=f"{random.choice(kill_options)}", color="#DC143C")
        embed.add_field(name="\u200b", value=f"*<@{sender}> killed <@{recipient}>*", inline=True)
        embed.set_footer(text=f"{kills} vs. {killeds}")
        await ctx.respond(embed)


def load(bot: lightbulb.BotApp):
    bot.command(kill)


def unload(bot: lightbulb.BotApp):
    bot.remove_command(bot.get_slash_command("kill"))
