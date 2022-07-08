import hikari
from dotenv import load_dotenv
import os

load_dotenv()

bot = hikari.GatewayBot(token=os.environ.get("bot_token"))
bot.run()

