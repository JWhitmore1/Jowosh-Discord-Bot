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
        db.execute("UPDATE economy SET dayclaim = 0")

    if datetime.strftime(datetime.now(),"%M") == "00":
        db = get_db()
        user_data = db.execute("SELECT id, bankbal, interest, maxbal FROM economy").fetchall()

        for user in user_data:
            id = user[0]
            bank_bal = user[1]
            interest = user[2]
            max_bal = user[3]

            new_bal = round(bankbal * interest, 2)

            if new_bal > max_bal:
                db.execute("UPDATE economy SET bankbal = ? WHERE id = ?", (max_bal, id))
            else:
                db.execute("UPDATE economy SET bankbal = ? WHERE id = ?", (new_bal, id))

            db.commit()


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(daily_plugin)
