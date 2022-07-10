import hikari
import lightbulb
import os
from dotenv import load_dotenv


def create_bot() -> lightbulb.BotApp:
    load_dotenv()
    bot = lightbulb.BotApp(
        token=os.environ.get("bot_token"),
        default_enabled_guilds=(853171732319174667, 995308486088994937)
    )

    bot.load_extensions_from("./commands")

    return bot


freak = create_bot()


@freak.listen(hikari.GuildMessageCreateEvent)
async def print_message(event):
    # print(event.content)
    if event.is_bot or not event.content:
        return

    if event.content.startswith("hi jowosh"):
        await event.message.respond("Hello!! ^-^")

freak.run()
