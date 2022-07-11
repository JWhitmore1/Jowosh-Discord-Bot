import hikari
import lightbulb
import os
from dotenv import load_dotenv
from db import initialise


def create_bot() -> lightbulb.BotApp:
    load_dotenv()
    bot = lightbulb.BotApp(
        token=os.environ.get("bot_token"),
        default_enabled_guilds=(int(os.environ.get("guild_id")))
    )

    bot.load_extensions_from("./commands")

    return bot


freak = create_bot()
initialise()


@freak.listen(hikari.GuildMessageCreateEvent)
async def print_message(event):
    # print(event.content)
    if event.is_bot or not event.content:
        return

    if event.content.startswith("hi jowosh"):
        await event.message.respond("Hello!! ^-^")
    elif event.content.startswith("my balls are tooo big???!? :/"):
        await event.message.respond("send pics lmao")

freak.run()
