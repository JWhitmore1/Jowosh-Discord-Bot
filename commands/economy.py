import hikari
import lightbulb
import random
from datetime import datetime
from db import get_db, check_id
from datetime import datetime
from hikari import Embed


econ_plugin = lightbulb.Plugin("economy")


def timedelta(reset):
    curr = (int(datetime.strftime(datetime.now(),"%I")) * 60) + int(datetime.strftime(datetime.now(),"%M"))
    if curr > 720:
        deltaM = (720 - curr) + (reset * 60)
    else:
        deltaM = (reset * 60) - curr

    hour = str(int(deltaM / 60))
    minute = str(deltaM % 60)

    return f"{hour}h {minute}m"


@lightbulb.command('daily', 'Claim your daily gold.')
@lightbulb.implements(lightbulb.SlashCommand)
async def daily(ctx):
    id = ctx.member.id
    db = get_db()

    if int(db.execute("SELECT dayclaim FROM economy WHERE ID = ?", (id,)).fetchone()[0]) == 0:
        check_id(id, db)
        current = int(db.execute("SELECT gold FROM economy WHERE ID = ?", (id,)).fetchone()[0])
        
        mean = 150
        sd = 50
        prefix = [":skull_crossbones:", 
                  "That's an L.", 
                  "Unlucky...", 
                  "Nice!", 
                  "Absolutely Huge!", 
                  "You lucky as hell!!", 
                  "The entire universe just conspiered to give you a bad day (there is a 0.00135% chance of this happening)"]

        amount = int(round(random.normalvariate(mean, sd), 0))
        
        if amount < 0: i = 6
        elif amount < (mean - (2 * sd)): i = 0
        elif amount < (mean - sd): i = 1
        elif amount < (mean): i = 2
        elif amount < (mean + sd): i = 3
        elif amount < (mean + (2 * sd)): i = 4
        else: i = 5

        db.execute('UPDATE economy SET gold = ? WHERE ID = ?', ((current + amount), id))
        db.execute('UPDATE economy SET dayclaim = 1 WHERE ID = ?', (id,))
        db.commit()

        await ctx.respond(f":coin: | {prefix[i]} You got {amount} gold")
    else:
        await ctx.respond(f"You have already claimed in this period.\nYou can claim again in **{timedelta(6)}**.")


@lightbulb.command('balance', 'View your current balance.')
@lightbulb.implements(lightbulb.SlashCommand)
async def balance(ctx):
    id = ctx.member.id
    db = get_db()
    bal = db.execute("SELECT gold, bankbal FROM economy WHERE id = ?", (id,)).fetchone()
    print(bal[0], bal[1])
    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


@lightbulb.command('bank info', 'view your bank account info')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    bank = db.execute("SELECT bankbal, maxbal, interest FROM economy WHERE id = ?", (id,)).fetchone()

    info = hikari.Embed(title="Bank Info", color="#FFD700")
    info.add_field(name="** **", value=f"There is currently **{bank[0]}** gold in your account")
    info.add_field(name="** **", value=f"")

    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


@lightbulb.command('bank deposit', 'deposit gold into your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    bank = db.execute("SELECT bankbal, banklvl, bankclaim FROM economy WHERE id = ?", (id,)).fetchone()
    print(bank[0], bank[1])  
    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


@lightbulb.command('bank claim', 'claim the interest from your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    bank = db.execute("SELECT bankbal, banklvl, bankclaim FROM economy WHERE id = ?", (id,)).fetchone()
    print(bank[0], bank[1])  
    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


@lightbulb.command('bank upgrade balance', 'upgrade the max balance of your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    bank = db.execute("SELECT bankbal, banklvl, bankclaim FROM economy WHERE id = ?", (id,)).fetchone()
    print(bank[0], bank[1])  
    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


@lightbulb.command('bank upgrade interest', 'upgrade interest your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    bank = db.execute("SELECT bankbal, banklvl, bankclaim FROM economy WHERE id = ?", (id,)).fetchone()
    print(bank[0], bank[1])  
    await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(econ_plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(econ_plugin)