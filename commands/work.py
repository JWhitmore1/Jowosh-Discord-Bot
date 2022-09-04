import hikari
import lightbulb
import random
import time
from db import get_db, check_econ_id
import requests
import json
import os


plugin = lightbulb.Plugin("Work")

maths_server_base_url = os.environ.get("maths_problem_gen_api_url", "http://localhost:8000")


def build_row(rest, choice_count, answer, level):
    row = rest.build_action_row()
    letters = ["a", "b", "c", "d"]
    for i in range(choice_count):
        if i == answer:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"answer_{level}")
        else:
            button = row.add_button(hikari.ButtonStyle.PRIMARY, f"choice_{i}_{level}")
        button.set_label(letters[i])
        button.add_to_container()
    return row


def fetch_question(level):
    response = json.loads(requests.get("http://localhost:8000/rand-problem").text)
    problem_url = response["problem_url"]
    answer = response["answer"]
    choice_urls = response["choice_urls"]

    urls = [hikari.files.URL(f"http://localhost:8000{url}") for url in [problem_url] + choice_urls]
    return [urls, choice_urls, answer]

async def send_problem(respond, level, rest):
    try:
        response = json.loads(requests.get(f"{maths_server_base_url}/rand-problem?level={level}").text)
        problem_url = response["problem_url"]
        answer = response["answer"]
        choice_urls = response["choice_urls"]

        urls = [hikari.files.URL(f"{maths_server_base_url}{endpoint}") for endpoint in [problem_url] + choice_urls]
        buttons = build_row(rest, len(choice_urls), answer, level)
        await respond("", attachments=urls, component=buttons)
    except Exception as e:
        await respond(f"Failed to load problem: {e}")

@plugin.command()
@lightbulb.option('level', 'what level of math would you like to complete', type=int, min_value=1, max_value=2, default=1)
@lightbulb.command('math', 'earn gold by doing maths!')
@lightbulb.implements(lightbulb.SlashCommand)
async def math(ctx):
    db = get_db()
    id = ctx.member.id
    check_econ_id(id, db)

    response = await ctx.respond("Loading...")
    message = await response.message()
    await send_problem(message.edit, ctx.options.level, ctx.bot.rest)


@plugin.listener(hikari.InteractionCreateEvent)
async def on_component_interaction(event: hikari.InteractionCreateEvent) -> None:
    # Filter out all unwanted interactions
    if not isinstance(event.interaction, hikari.ComponentInteraction):
        return

    button_id = event.interaction.custom_id
    if button_id.startswith("answer_"):
        level = int(button_id.split("_")[-1])
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'Correct :thumbsup: Loading next problem...')
        await send_problem(event.interaction.execute, level, event.interaction.app.rest)
        await event.interaction.edit_initial_response('Correct :thumbsup:')
    elif event.interaction.custom_id.startswith("choice_"):
        level = int(button_id.split("_")[-1])
        await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, 'dumbass. Loading next problem...')
        await send_problem(event.interaction.execute, level, event.interaction.app.rest)
        await event.interaction.edit_initial_response('dumbass')


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
