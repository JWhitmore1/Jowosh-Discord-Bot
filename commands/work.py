import hikari
import lightbulb
import random
import time
from db import get_db, check_econ_id
import requests
import json


plugin = lightbulb.Plugin("Work")


def build_row(bot, choice_count, answer):
    row = bot.rest.build_action_row()
    letters = ["a", "b", "c", "d"]
    for i in range(choice_count):
        if i == answer:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"answer")
        else:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"choice_{i}")
        button.set_label(letters[i])
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
        response = json.loads(requests.get("http://localhost:8000/rand-problem").text)
        problem_url = response["problem_url"]
        answer = response["answer"]
        choice_urls = response["choice_urls"]

        urls = [hikari.files.URL(f"http://localhost:8000{url}") for url in [problem_url] + choice_urls]
        buttons = build_row(ctx.bot, len(choice_urls), answer)
        await ctx.respond("", attachments=urls, component=buttons)


@plugin.listener(hikari.InteractionCreateEvent)
async def on_component_interaction(event: hikari.InteractionCreateEvent) -> None:
    # Filter out all unwanted interactions
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    if event.interaction.custom_id == "answer":
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'Correct :thumbsup:')
    elif event.interaction.custom_id.startswith("choice_"):
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'dumbass')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
