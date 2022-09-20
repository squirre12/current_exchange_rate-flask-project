from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("CryptonatorApi")

    def _update_rate(self, current_rate):
        rate = self._get_crypto_rate(current_rate.from_currency, current_rate.to_currency)
        return rate

    def _get_crypto_rate(self, from_currency, to_currency):
        crypto_aliases_map = {840: "usd", 980: "uah", 643: "rur", 1000: "btc"}

        if from_currency not in crypto_aliases_map:
            raise ValueError("Invalid from_currency: {}".format(from_currency))
        if to_currency not in crypto_aliases_map:
            raise ValueError("Invalid from_currency: {}".format(from_currency))

        response = self._send_request(
            url="https://api.cryptonator.com/api/ticker/{}-{}".format(crypto_aliases_map[from_currency],
                                                                      crypto_aliases_map[to_currency]),
            method='get')
        response_data = response.json()
        self.log.debug("Crypto response: {}".format(response_data))
        usd_rate = self._find_rate(response_data)

        return usd_rate

    @staticmethod
    def _find_rate(response_data):
        return float(response_data['ticker']['price'])
