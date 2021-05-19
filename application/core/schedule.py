from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from datetime import datetime
from config import Config

from application.bot import publishing


_rating_trigger = CronTrigger(day_of_week='sun', hour=12, timezone='Asia/Tashkent')
_scheduler = BackgroundScheduler()
_scheduler.add_jobstore('sqlalchemy', url=Config.APSCHEDULER_DATABASE_URI)
_scheduler.start()
_scheduler.add_job(publishing.publish_rating, _rating_trigger, id='rating', replace_existing=True)


def add_test_to_publish(test_id: int, date_time: datetime):
    trigger = DateTrigger(run_date=date_time, timezone='Asia/Tashkent')
    _scheduler.add_job(publishing.publish_test, trigger, [test_id], id='test_'+str(test_id))


def remove_test_from_publishing(test_id: int):
    try:
        _scheduler.remove_job('test_'+str(test_id))
    except JobLookupError:
        pass


def update_test_date_publish(test_id: int, date_time: datetime):
    try:
        remove_test_from_publishing(test_id)
    except JobLookupError:
        pass
    add_test_to_publish(test_id, date_time)


def stop_all_jobs():
    _scheduler.remove_all_jobs()
    _scheduler.pause()


def pause_scheduler():
    _scheduler.pause()


def resume_scheduler():
    _scheduler.resume()


def start_scheduler():
    _scheduler.add_job(publishing.publish_rating, _rating_trigger, replace_existing=True, id='rating')
