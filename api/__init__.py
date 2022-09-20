import traceback
import importlib

import requests

from config import LOGGER_CONFIG, logging, HTTP_TIMEOUT
from models import CurrentRate, peewee_datetime, ApiLog, ErrorLog

fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])


def update_rate(from_currency, to_currency):
    current_rate = CurrentRate.select().where(CurrentRate.from_currency == from_currency,
                                              CurrentRate.to_currency == to_currency).first()
    module = importlib.import_module('api.{}'.format(current_rate.module))
    module.Api().update_rate(current_rate)


class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger(logger_name)
        self.log.addHandler(fh)
        self.log.setLevel(LOGGER_CONFIG["level"])

    def update_rate(self, current_rate):
        self.log.info("Started update for: {} ".format(current_rate))
        self.log.debug("rate before: {}".format(current_rate))
        current_rate.rate = self._update_rate(current_rate)
        current_rate.update_date = peewee_datetime.datetime.now()
        current_rate.save()

        self.log.debug("rate after: {}".format(current_rate))
        self.log.info("Finished update for: {}".format(current_rate))

    def _update_rate(self, current_rate):
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        log = ApiLog(requests_data=data, requests_url=url, requests_method=method, requests_headers=headers)
        try:
            response = self._send(method=method, url=url, data=data, headers=headers)
            log.response_text = response.text
            return response
        except Exception as error:
            self.log.exception("Error during request sending")
            log.error = str(error)
            ErrorLog.create(request_data=data, request_url=url, request_method=method, error=str(error),
                            traceback=traceback.format_exc(chain=False))
            raise
        finally:
            log.finished = peewee_datetime.datetime.now()
            log.save()

    @staticmethod
    def _send(url, method, data=None, headers=None):
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT)
