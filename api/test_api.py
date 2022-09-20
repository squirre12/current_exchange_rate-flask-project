import logging

from config import LOGGER_CONFIG
from models import CurrentRate

log = logging.getLogger("TestApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])


def update_current_rate(from_currency, to_currency):
    log.info("Started update for: {} => {}".format(from_currency, to_currency))
    current_rate = CurrentRate.select().where(CurrentRate.from_currency == from_currency,
                                              CurrentRate.to_currency == to_currency).first()
    log.debug("rate before: {}".format(current_rate))
    current_rate.rate += 0.01
    current_rate.save()
    log.debug("rate after: {}".format(current_rate))
    log.info("Finished update for: {} => {}".format(from_currency, to_currency))
