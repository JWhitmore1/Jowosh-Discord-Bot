import lightbulb
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


reset_time = 6
daily_plugin = lightbulb.Plugin("Daily")
sched = AsyncIOScheduler()
sched.start()


@sched.scheduled_job(CronTrigger(minute="*/1"))
async def daily_reset() -> None:
    if int(datetime.strftime(datetime.now(),"%I")) == reset_time:
        # reset all users dayclaim and bankclaim
        pass
        # await daily_plugin.app.rest.create_message(995308487011737662, "Resetting fr")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(daily_plugin)
