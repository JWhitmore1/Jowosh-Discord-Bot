from ast import Try
import hikari
import lightbulb
import random
from datetime import datetime
from db import get_db, check_econ_id
from datetime import datetime
from hikari import Embed

plugin = lightbulb.Plugin("Economy")


def generateEconEmbed(type, gold, bal, blvl, maxb, ilvl, i, action, ctx):
    e = hikari.Embed(title=f"{str((ctx.member)).split('#')[0]}'s bank", color="#FFD700")
    if type == 'info':
        e.add_field(name="Balances", value=f"Wallet: **{gold}** gold\n Bank: **{bal}** gold")
        e.add_field(name="Leveling", value=f"Balance level **{blvl}**: **{maxb}** max gold \n Interest level **{ilvl}**:  **{p(i)}%**")
        e.add_field(name="Earning", value=f"You will accrue **{round(bal*(i - 1), 2)}** gold in the next hour")
        e.add_field(name="** **", value="** **")
    
    if type == 'action':
        if action == 'deposit':
            e.add_field(name="** **", value=f"Successfully deposited **{ctx.options.amount}** gold into your bank!")
            e.add_field()
        if action == 'withdraw':
            pass
        if action == 'upgradeB':
            pass
        if action == 'upgradeI':
            pass

    return e


def timedelta(reset):
    curr = (int(datetime.strftime(datetime.now(),"%I")) * 60) + int(datetime.strftime(datetime.now(),"%M"))
    if curr > 720:
        delta_mins = (720 - curr) + (reset * 60)
    else:
        delta_mins = (reset * 60) - curr

    hour = str(int(delta_mins / 60))
    minute = str(delta_mins % 60)

    return f"{hour}h {minute}m"


def p(rate):
    return round((rate - 1)*100, 3)


def getIntLevel(curr_interest):
    return round((curr_interest - 1.01)/0.001, 0)


def getIntPrice(level):
    return round(100*(level**3), 2)


def getBalLevel(curr_max):
    return (curr_max - 50)/50


def getBalPrice(level):
    return 500*(level)**2


@plugin.command()
@lightbulb.command('daily', 'Claim your daily gold.')
@lightbulb.implements(lightbulb.SlashCommand)
async def daily(ctx):
    id = ctx.member.id
    db = get_db()
    check_econ_id(id, db)

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
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT bankbal, maxbal, interest, gold FROM economy WHERE id = ?", (id,)).fetchone()
    balLevel = int(getBalLevel(bankinfo[1]))
    intLevel = int(getIntLevel(bankinfo[2]))

    info = generateEconEmbed("info", bankinfo[3], bankinfo[0], balLevel, bankinfo[1], intLevel, bankinfo[2], None, ctx)

    await ctx.respond(info)


@plugin.command()
@lightbulb.option('amount', "how much gold do you want to deposit", type=int, min_value=0)
@lightbulb.command('deposit', 'deposit gold into your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def deposit(ctx):
    amount = ctx.options.amount
    id = ctx.member.id
    db = get_db()
    check_econ_id(id, db)
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
    check_econ_id(id, db)
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
@lightbulb.option('action', 'what would you like to upgrade', choices=('balance', 'interest'))
@lightbulb.command('upgrade', 'upgrade the interest of your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def upgradeInterest(ctx):
    id = ctx.member.id
    db = get_db()
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT gold, maxbal, interest FROM economy WHERE id = ?", (id,)).fetchone()
    gold = bankinfo[0]

    if ctx.options.action == 'balance':
        
        int_level = getIntLevel(bankinfo[2])
        int_price = int(getIntPrice(int_level))

        if int_price <= gold:
            newInterest = round(bankinfo[2] + 0.001, 3)
            newLevel = int_level + 1
            newGold = gold - int_price
            db.execute("UPDATE economy SET interest = ?, gold = ? WHERE id = ?", (newInterest, newGold, id))
            db.commit()
            await ctx.respond(f"Upgraded your interest level to **{newLevel}**, you now have **{p(newInterest)}%** interest!\nThe next upgrade will cost **{getIntPrice(newLevel)}** gold")
        else:
            await ctx.respond(f"You don't have enough money to purchase this! This upgrade costs **{int_price}** gold")
    
    if ctx.options.action == 'interest':
        
        bal_level = getBalLevel(bankinfo[1])
        bal_price = int(getBalPrice(bal_level))

        if bal_price <= gold:
            newBal = bankinfo[1] + 50
            newLevel = bal_level + 1
            newGold = gold - bal_price
            db.execute("UPDATE economy SET maxbal = ?, gold = ? WHERE id = ?", (newBal, newGold, id))
            db.commit()
            await ctx.respond(f"Upgraded your balance level to **{newLevel}**, you can now hold **{newBal}** gold!\nThe next upgrade will cost **{getBalPrice(newLevel)}** gold")
        else:
            await ctx.respond(f"You do not have enough gold in your wallet to upgrade this! The upgrade costs **{bal_price}** gold.")


@plugin.command()
@lightbulb.app_command_permissions(perms=8)
@lightbulb.option('amount', 'how much gold do you want to set', type=int, min_value=0)
@lightbulb.option('user', 'which user do you want to set', hikari.User, required=False)
@lightbulb.command('set-gold', 'set gold in your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def set(ctx):
    amount = ctx.options.amount
    if ctx.options.user != None:
        recipitent = ctx.options.user.id
    else:
        recipitent = ctx.member.id
    
    db = get_db()
    check_econ_id(recipitent, db)
    db.execute("UPDATE economy SET gold = ? WHERE id = ?", (amount, recipitent)).fetchone()
    db.commit()
    await ctx.respond(f"set wallet to {amount}")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)