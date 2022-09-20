import xml.etree.ElementTree as ET


from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("CbrApi")

    def _update_rate(self, current_rate):
        rate = self._get_cbr_rate(current_rate.from_currency)
        return rate

    def _get_cbr_rate(self, from_currency):
        response = self._send_request(url="https://www.cbr-xml-daily.ru/daily.xml", method='get')
        self.log.debug("response.encoding: {}".format(response.encoding))
        response_xml = response.text
        self.log.debug("response.text: %s" % response_xml.encode())
        usd_rate = self._find_rate(response_xml, from_currency)

        return usd_rate

    def _find_rate(self, response_data, from_currency):
        root = ET.fromstring(response_data)
        valutes = root.findall("Valute")

        cbr_valute_map = {840: "USD"}
        currency_cbr_alias = cbr_valute_map[from_currency]

        for valute in valutes:
            if valute.find("CharCode").text == currency_cbr_alias:
                return float(valute.find("Value").text.replace(",", "."))

        raise ValueError("Invalid CBR response: USD not found")


