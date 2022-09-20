import unittest

import requests

import xml.etree.ElementTree as ET
import api
import models
from api import test_api


class Test(unittest.TestCase):
    def setUp(self) -> None:
        models.init_db()

    def test_main(self):
        current_rate = models.CurrentRate.get(id=1)
        self.assertEqual(current_rate.rate, 1.0)
        test_api.update_current_rate(840, 980)
        current_rate = models.CurrentRate.get(id=1)

        self.assertEqual(current_rate.rate, 1.01)

    def test_privat_btc(self):
        current_rate = models.CurrentRate.get(from_currency=1000, to_currency=840)
        update_before = current_rate.update_date
        self.assertEqual(current_rate.rate, 1.0)
        api.update_rate(1000, 840)
        current_rate = models.CurrentRate.get(from_currency=1000, to_currency=840)
        update_after = current_rate.update_date

        self.assertGreaterEqual(current_rate.rate, 5000)
        self.assertGreaterEqual(update_after, update_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.requests_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        self.assertIsNotNone(api_log.response_text)
        self.assertIn('{"ccy":"USD","base_ccy":"UAH",', api_log.response_text)


    def test_cbr(self):
        current_rate = models.CurrentRate.get(from_currency=840, to_currency=643)
        update_before = current_rate.update_date
        self.assertEqual(current_rate.rate, 1.0)
        api.update_rate(840, 643)
        current_rate = models.CurrentRate.get(from_currency=840, to_currency=643)
        update_after = current_rate.update_date

        self.assertGreaterEqual(current_rate.rate, 40)
        self.assertGreaterEqual(update_after, update_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.requests_url, "https://www.cbr-xml-daily.ru/daily.xml")
        self.assertIsNotNone(api_log.response_text)

    def test_crypto(self):
        current_rate = models.CurrentRate.get(from_currency=1000, to_currency=980)
        update_before = current_rate.update_date
        self.assertEqual(current_rate.rate, 1.0)
        api.update_rate(1000, 980)
        current_rate = models.CurrentRate.get(from_currency=1000, to_currency=980)
        update_after = current_rate.update_date

        self.assertGreaterEqual(current_rate.rate, 40)
        self.assertGreaterEqual(update_after, update_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.requests_url, "https://www.cbr-xml-daily.ru/daily.xml")
        self.assertIsNotNone(api_log.response_text)

    def test_html_rates(self):
        r = requests.get("http://localhost:5000/rates")
        print(r.text)
        self.assertTrue(r.ok)
        self.assertIn('<table border="1"', r.text)
        root = ET.fromstring(r.text)
        body = root.find("body")
        self.assertIsNotNone(body)
        table = root.find("table")
        self.assertIsNotNone(table)
        rows = root.find("tr")
        self.assertIsNotNone(rows)


if __name__ == '__main__':
    unittest.main()
