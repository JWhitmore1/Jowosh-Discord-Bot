from doctest import REPORT_CDIFF
import hikari
import lightbulb
import random
import time
from db import get_db, check_econ_id


plugin = lightbulb.Plugin("Work")


@plugin.command()
@lightbulb.option('level', 'what level of math would you like to complete', type=int, min_value=1, max_value=4)
@lightbulb.command('math-work', 'earn gold by doing maths!')
@lightbulb.implements(lightbulb.SlashCommand)
async def math(ctx):
    db = get_db()
    id = ctx.member.id
    channel = ctx.channel_id
    check_econ_id(id, db)

    if ctx.options.level == 1:
        numbers = [random.randint(1, 49), random.randint(1, 49)]
        operator = random.choice(["+", "-"])
        
        if operator == "+": answer = numbers[0] + numbers[1]
        if operator == "-": answer = numbers[0] - numbers[1]
        
        await ctx.respond(f"{numbers[0]} {operator} {numbers[1]} = ?")

        timeout = time.time() + 10

        def check(m):
            return m.content is not None and m.channel == channel

        response = await hikari.impl.GatewayBot.wait_for(hikari.impl.GatewayBot, hikari.MessageCreateEvent, timeout=20)
        print(response)

        # response = await plugin.listener(hikari.MessageCreateEvent, responseListener(id, channel))
        # while time.time() < timeout:
        #     if response != None:
        #         break
            
        if response == None:
            await ctx.respond("you did not reply in time")
        else:
            content = response.content
            print(content)

            if content == answer:
                await ctx.respond("Correct")
            else:
                await ctx.respond("Incorrect")


# @plugin.listener(hikari.MessageCreateEvent)
async def responseListener(event, id, channel):
    try:
        if event.author_id == id and event.channel_id == channel:
            print("message recieved")
            return(event)
    except TypeError:
        print(event.content)
        

@plugin.command()
@lightbulb.command('stop', 'stop task')
@lightbulb.implements(lightbulb.SlashCommand)
async def stop(ctx):
    ctx.respond("stop, please!")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)