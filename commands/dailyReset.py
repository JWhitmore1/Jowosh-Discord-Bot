import lightbulb
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from db import get_db


reset_time = "0600"
daily_plugin = lightbulb.Plugin("Daily")
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job(CronTrigger(minute="*/1"))
async def daily_reset() -> None:
    if datetime.strftime(datetime.now(),"%I%M") == reset_time:
        print("resetting")
        # reset all users dayclaim and bankclaim
        db = get_db()
        db.execute("UPDATE economy SET dayclaim = 0, bankclaim = 0")
        pass
        # await daily_plugin.app.rest.create_message(995308487011737662, "Resetting fr")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(daily_plugin)
