from msilib.schema import Component
import hikari
import lightbulb
import random
import time
from db import get_db, check_econ_id


plugin = lightbulb.Plugin("Work")


def build_row(bot, options, answer):
    row = bot.rest.build_action_row()
    for i in range(len(options)):
        if options[i] == answer:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"answer")
        else:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"option_{i}")
        button.set_label(str(options[i]))
        button.add_to_container()
    return row


@plugin.command()
@lightbulb.option('level', 'what level of math would you like to complete', type=int, min_value=1, max_value=4)
@lightbulb.command('math', 'earn gold by doing maths!')
@lightbulb.implements(lightbulb.SlashCommand)
async def math(ctx):
    db = get_db()
    id = ctx.member.id
    check_econ_id(id, db)

    if ctx.options.level == 1:
        numbers = [random.randint(1, 49), random.randint(1, 49)]
        operator = random.choice(["+", "-"])
        
        if operator == "+": 
            answer = numbers[0] + numbers[1]
        if operator == "-": 
            answer = numbers[0] - numbers[1]

        ans_options = [answer, answer + random.randint(1, 5), answer - random.randint(1, 5), answer + random.randint(5, 10)]
        random.shuffle(ans_options)

        buttons = build_row(ctx.bot, ans_options, answer)
        await ctx.respond(f"{numbers[0]} {operator} {numbers[1]} = ", component=buttons)


@plugin.listener(hikari.InteractionCreateEvent)
async def on_component_interaction(event: hikari.InteractionCreateEvent) -> None:
    # Filter out all unwanted interactions
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    if event.interaction.custom_id == "answer":
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'Correct :thumbsup:')
    else:
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'dumbass')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)