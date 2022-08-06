from ast import Try
import hikari
import lightbulb
import random
from datetime import datetime
from db import get_db, check_id
from datetime import datetime
from hikari import Embed

plugin = lightbulb.Plugin("Economy")


def timedelta(reset):
    curr = (int(datetime.strftime(datetime.now(),"%I")) * 60) + int(datetime.strftime(datetime.now(),"%M"))
    if curr > 720:
        deltaM = (720 - curr) + (reset * 60)
    else:
        deltaM = (reset * 60) - curr

    hour = str(int(deltaM / 60))
    minute = str(deltaM % 60)

    return f"{hour}h {minute}m"


def p(rate):
    return round((rate - 1)*100, 3)


def getIntLevel(curr_interest):
    return round((curr_interest - 1.01)/0.001, 0)


def getIntPrice(level):
    return round(100*(level**3), 2)


@plugin.command()
@lightbulb.command('daily', 'Claim your daily gold.')
@lightbulb.implements(lightbulb.SlashCommand)
async def daily(ctx):
    id = ctx.member.id
    db = get_db()
    check_id(id, db)

    if int(db.execute("SELECT dayclaim FROM economy WHERE ID = ?", (id,)).fetchone()[0]) == 0:
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


@plugin.command()
@lightbulb.command('bank', 'view your bank account info')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    id = ctx.member.id
    db = get_db()
    check_id(id, db)
    bank = db.execute("SELECT bankbal, maxbal, interest, gold FROM economy WHERE id = ?", (id,)).fetchone()
    intamount = round(bank[0]*(bank[2] - 1), 2)

    info = hikari.Embed(title=f":bank: | Jowosh Bank", color="#FFD700")
    info.add_field(name="Bank Info\n", value=f"There is currently **{bank[3]}** gold in your wallet, and **{bank[0]}** gold in your bank account.")
    info.add_field(name="** **", value=f"Your maximum balance is level **___** and can hold **{bank[1]}** gold!")
    info.add_field(name="** **", value=f"Your hourly interest rate is level **{getIntLevel(bank[2])}**, with **{p(bank[2])}%**. You will accrue **{intamount}** gold in the next hour!")
    info.add_field(name="** **", value="** **")
    info.set_footer(text="upgrade bank with /upgradeblahblahsuckmyfuckingdickihatethis")

    await ctx.respond(info)


@plugin.command()
@lightbulb.option('amount', "how much gold do you want to deposit", type=int, min_value=0)
@lightbulb.command('deposit', 'deposit gold into your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def deposit(ctx):
    amount = ctx.options.amount
    id = ctx.member.id
    db = get_db()
    check_id(id, db)
    bankinfo = db.execute("SELECT gold, maxbal, bankbal FROM economy WHERE id = ?", (id,)).fetchone()
    if bankinfo[0] >= amount:
        new_amount = bankinfo[2] + amount
        if new_amount > bankinfo[1]:
            await ctx.respond("You cannot deposit more than the max value!")
        else:
            db.execute("UPDATE economy SET bankbal = ?, gold = ? WHERE ID = ?", (new_amount, bankinfo[0]-amount, id))
            db.commit()
            await ctx.respond(f"Successfully deposited **{amount}** gold.\nThere is now **{new_amount}** gold in your bank.")
    else:
        ctx.respond("You do not have enough gold to deposit! Broke lookin ass :skull:")


@plugin.command()
@lightbulb.option('amount', 'how much would you like to withdraw', type=int, min_value=0)
@lightbulb.command('withdraw', 'withdraw money from your bank')
@lightbulb.implements(lightbulb.SlashCommand)
async def withdraw(ctx):
    id = ctx.member.id
    amount = ctx.options.amount
    db = get_db()
    check_id(id, db)
    bankinfo = db.execute("SELECT gold, bankbal FROM economy WHERE id = ?", (id,)).fetchone()
    if amount <= bankinfo[1]:
        newGold = bankinfo[0]+amount
        newBankBal = bankinfo[1]-amount
        db.execute("UPDATE economy SET gold = ?, bankbal = ? WHERE id = ?", (newGold, newBankBal, id))
        await ctx.respond(f"*Cha Ching!* You withdrew **{amount}** gold!\nYou now have **{newGold}** gold in your wallet and **{newBankBal}** gold in your bank.")
        db.commit()
    else:
        await ctx.respond("There is not enough gold in your bank!")


@plugin.command()
@lightbulb.command('upgrade-balance', 'upgrade the max balance of your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def upgradeBalance(ctx):
    id = ctx.member.id
    db = get_db()
    check_id(id, db)

    bankinfo = db.execute("SELECT gold, maxbal, interest FROM economy WHERE id = ?", (id,)).fetchone()
    gold = bankinfo[0]
    int_level = getIntLevel(bankinfo[2])
    int_price = int(getIntPrice(int_level))

    if int_price <= bankinfo[0]:
        newInterest = round(bankinfo[2] + 0.001, 3)
        newLevel = int_level + 1
        newGold = gold - int_price
        db.execute("UPDATE economy SET interest = ?, gold = ? WHERE id = ?", (newInterest, newGold, id))
        db.commit()
        await ctx.respond(f"Upgraded your interest level to **{newLevel}**, you now have **{p(newInterest)}%** interest!\nThe next upgrade will cost **{getIntPrice(newLevel)}** gold")
    else:
        await ctx.respond(f"You don't have enough money to purchase this! This upgrade costs **{int_price}** gold")


@plugin.command()
@lightbulb.option('amount', "how much gold do you want to set", type=int, min_value=0)
@lightbulb.command('set', 'set gold in your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def set(ctx):
    amount = ctx.options.amount
    id = ctx.member.id
    db = get_db()
    check_id(id, db)
    db.execute("UPDATE economy SET gold = ? WHERE id = ?", (amount, id)).fetchone()
    db.commit()
    await ctx.respond(f"set your wallet to {amount}")

# @plugin.command()
# @lightbulb.command('bank upgrade interest', 'upgrade interest your bank account')
# @lightbulb.implements(lightbulb.SlashCommand)
# async def bank(ctx):
#     id = ctx.member.id
#     db = get_db()
#     bank = db.execute("SELECT bankbal, banklvl, bankclaim FROM economy WHERE id = ?", (id,)).fetchone()
#     print(bank[0], bank[1])  
#     await ctx.respond(f"You currently have **{str(bal[0])}** gold.\nYour bank has **{str(bal[1])}** gold.")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)