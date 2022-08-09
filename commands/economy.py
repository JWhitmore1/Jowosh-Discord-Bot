import hikari
import lightbulb
import random
from datetime import datetime
from db import get_db, check_econ_id
from datetime import datetime

plugin = lightbulb.Plugin("Economy")
intr_increment = 0.001
bal_increment = 50


def p(rate):
    return round((rate - 1)*100, 3)


def getIntLevel(curr_interest):
    return int(round((curr_interest - 1.01)/0.001, 0))


def getIntPrice(level):
    return round(100*(level**3), 2)


def getBalLevel(curr_max):
    return int((curr_max - 50)/50)


def getBalPrice(level):
    return 500*(level)**2


def timeUntil(reset):
    curr = (int(datetime.strftime(datetime.now(),"%I")) * 60) + int(datetime.strftime(datetime.now(),"%M"))
    if curr > 720:
        delta_mins = (720 - curr) + (reset * 60)
    else:
        delta_mins = (reset * 60) - curr

    hour = str(int(delta_mins / 60))
    minute = str(delta_mins % 60)

    return f"{hour}h {minute}m"


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
        await ctx.respond(f"You have already claimed in this period.\nYou can claim again in **{timeUntil(6)}**.")


@plugin.command()
@lightbulb.option('user', 'which users bank do you want to view', hikari.User, required=False)
@lightbulb.command('bank', 'view your bank account info')
@lightbulb.implements(lightbulb.SlashCommand)
async def bank(ctx):
    if ctx.options.user != None:
        id = ctx.options.user.id
        name = str(ctx.options.user).split('#')[0]
    else:
        id = ctx.member.id
        name = str(ctx.member).split('#')[0]
    db = get_db()
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT bankbal, maxbal, interest, gold FROM economy WHERE id = ?", (id,)).fetchone()
    balLevel = int(getBalLevel(bankinfo[1]))
    intLevel = int(getIntLevel(bankinfo[2]))
    newAmount = round(bankinfo[0]*(bankinfo[2]-1), 2)

    info = hikari.Embed(title=f"{name}'s bank", color="#FFD700")
    info.add_field(name="Balances", value=f"Wallet: **{bankinfo[3]}** gold\nBank: **{bankinfo[0]}** gold")
    info.add_field(name="Leveling", value=f"Balance level **{balLevel}:** **{bankinfo[1]}** max gold\nInterest level **{intLevel}:**  **{p(bankinfo[2])}%**")
    info.add_field(name="Earning", value=f"You will accrue **{newAmount}** gold every hour")

    await ctx.respond(info)


@plugin.command()
@lightbulb.option('amount', "how much gold do you want to deposit", type=int, min_value=0)
@lightbulb.command('deposit', 'deposit gold into your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def deposit(ctx):
    amount = ctx.options.amount
    id = ctx.member.id
    name = str(ctx.member).split('#')[0]
    db = get_db()
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT gold, maxbal, bankbal FROM economy WHERE id = ?", (id,)).fetchone()
    if bankinfo[0] >= amount:
        newBankBal = bankinfo[2] + amount
        if newBankBal > bankinfo[1]:
            await ctx.respond("You cannot deposit more than the max value!")
        else:
            db.execute("UPDATE economy SET bankbal = ?, gold = ? WHERE ID = ?", (newBankBal, bankinfo[0]-amount, id))
            db.commit()
            
            info = hikari.Embed(title=f"{name}'s bank", color="#FFD700")
            info.add_field(name="Deposit", value=f"Successfully deposited **{amount}** gold into your bank!\nBalance: **{bankinfo[2]} -> {newBankBal}** gold!")
            
            await ctx.respond(info)
    else:
        ctx.respond("You do not have enough gold to deposit! Broke lookin ass :skull:")


@plugin.command()
@lightbulb.option('amount', 'how much would you like to withdraw', type=int, min_value=0)
@lightbulb.command('withdraw', 'withdraw money from your bank')
@lightbulb.implements(lightbulb.SlashCommand)
async def withdraw(ctx):
    id = ctx.member.id
    amount = ctx.options.amount
    name = str(ctx.member).split('#')[0]
    db = get_db()
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT gold, bankbal FROM economy WHERE id = ?", (id,)).fetchone()
    if amount <= bankinfo[1]:
        newGold = bankinfo[0]+amount
        newBankBal = bankinfo[1]-amount
        db.execute("UPDATE economy SET gold = ?, bankbal = ? WHERE id = ?", (newGold, newBankBal, id))
        db.commit()

        info = hikari.Embed(title=f"{name}'s bank", color="#FFD700")
        info.add_field(name="Withdraw", value=f"Successfully withdrew **{amount}** from your bank!\nBalance: **{bankinfo[1]} -> {newBankBal}** gold!")
        
        await ctx.respond(info)
    else:
        await ctx.respond("There is not enough gold in your bank!")


@plugin.command()
@lightbulb.option('action', 'what would you like to upgrade', choices=('balance', 'interest'))
@lightbulb.command('upgrade', 'upgrade the interest of your bank account')
@lightbulb.implements(lightbulb.SlashCommand)
async def upgrade(ctx):
    id = ctx.member.id
    name = str(ctx.member).split('#')[0]
    db = get_db()
    check_econ_id(id, db)
    bankinfo = db.execute("SELECT gold, maxbal, interest FROM economy WHERE id = ?", (id,)).fetchone()
    gold = bankinfo[0]

    info = hikari.Embed(title=f"{name}'s bank", color="#FFD700")

    if ctx.options.action == 'interest':

        int_level = getIntLevel(bankinfo[2])
        int_price = int(getIntPrice(int_level))

        if int_price <= gold:
            newInterest = round(bankinfo[2] + intr_increment, 3)
            newLevel = int_level + 1
            newGold = gold - int_price
            db.execute("UPDATE economy SET interest = ?, gold = ? WHERE id = ?", (newInterest, newGold, id))
            db.commit()
            
            info.add_field(name="Upgrade", value=f"Successfully upgraded interest to to **{p(newInterest)}%**!\n\nLevel: **{int_level} -> {newLevel}**\nInterest: **{p(bankinfo[2])} -> {p(newInterest)}%**")

            await ctx.respond(info)
        else:
            await ctx.respond(f"You do not have enough gold in your wallet to upgrade this! The upgrade costs **{int_price}** gold.")
    
    if ctx.options.action == 'balance':
        
        bal_level = getBalLevel(bankinfo[1])
        bal_price = int(getBalPrice(bal_level))

        if bal_price <= gold:
            newBal = bankinfo[1] + bal_increment
            newLevel = bal_level + 1
            newGold = gold - bal_price
            db.execute("UPDATE economy SET maxbal = ?, gold = ? WHERE id = ?", (newBal, newGold, id))
            db.commit()
            
            info.add_field(name="Upgrade", value=f"Successfully upgraded max balance to **{newBal}**!\n\nLevel: **{bal_level} -> {newLevel}**\nMax Balance: **{bankinfo[1]} -> {newBal}**")

            await ctx.respond(info)
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
        recipient = ctx.options.user.id
    else:
        recipient = ctx.member.id
    
    db = get_db()
    check_econ_id(recipient, db)
    db.execute("UPDATE economy SET gold = ? WHERE id = ?", (amount, recipient)).fetchone()
    db.commit()
    await ctx.respond(f"set wallet to {amount}")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)