from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("PrivatApi")

    def _update_rate(self, current_rate):
        rate = self._get_private_rate(current_rate.from_currency)
        return rate

    def _get_private_rate(self, from_currency):
        response = self._send_request(url="https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11",
                                      method='get')
        response_json = response.json()
        self.log.debug("Private response: {}".format(response_json))
        usd_rate = self._find_rate(response_json, from_currency)

        return usd_rate

    @staticmethod
    def _find_rate(response_data, from_currency):
        privat_aliases_map = {840: "USD", 1000: "BTC"}

        if from_currency not in privat_aliases_map:
            raise ValueError("Invalid from_currency: {}".format(from_currency))

        currency_alias = privat_aliases_map[from_currency]
        for e in response_data:
            if e["ccy"] == currency_alias:
                return float(e["sale"])

        raise ValueError("invalid Privat response: USD not found")
