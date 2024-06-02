async def add_scheduler_jobs():
    from app import scheduler
    from app.vbb.service import remove_is_notified

    from apscheduler.triggers.cron import CronTrigger

    scheduler.add_job(remove_is_notified, CronTrigger(hour=0, minute=0))

    scheduler.start()
