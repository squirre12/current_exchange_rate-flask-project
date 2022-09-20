from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

import api
from models import CurrentRate

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def updates_rates():
    print("Jobs started at: {}".format(datetime.now()))
    rates = CurrentRate.select()
    for rate in rates:
        try:
            api.update_rate(rate.from_currency, rate.to_currency)
        except Exception as ex:
            print(ex)
    print("Jobs finished at: {}".format(datetime.now()))


print("Before {}".format(datetime.now()))
sched.start()
