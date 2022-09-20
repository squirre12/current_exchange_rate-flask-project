from datetime import datetime

import xmltodict as xmltodict
from flask import render_template, make_response, request, jsonify, redirect, url_for

import api
from models import CurrentRate, ApiLog


class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwds):
        try:
            return self._call(*args, **kwds)
        except Exception as ex:
            return make_response(str(ex), 500)

    def _call(self, *args, **kwds):
        raise NotImplemented("_call")


class ViewAllRates(BaseController):
    def _call(self):
        rates = CurrentRate.select()
        return render_template("CurrentRate.html", rates=rates)


class GetApiRates(BaseController):
    def _call(self, fmt):
        rates = CurrentRate.select()
        rates = self._filter(rates)

        if fmt == "json":
            return self._get_json(rates)
        elif fmt == "xml":
            return self._get_xml(rates)
        raise ValueError("Unknown fmt: {}".format(fmt))

    def _filter(self, rates):
        args = self.request.args

        if 'from_currency' in args:
            rates = rates.where(CurrentRate.from_currency == args.get("from_currency"))

        if "to_currency" in args:
            rates = rates.where(CurrentRate.to_currency == args.get("to_currency"))

        return rates

    def _get_xml(self, rates):
        d = {"rates": {"rate": [
            {"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in rates]}}
        return make_response(xmltodict.unparse(d), {'Content-Type': 'text/xml'})

    def _get_json(self, rates):
        return jsonify([{"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in rates])


class UpdateRates(BaseController):
    def _call(self, from_currency, to_currency):
        if not from_currency and not to_currency:
            self._update_all()

        elif from_currency and to_currency:
            self._update_rate(from_currency, to_currency)

        else:
            raise ValueError("from_currency and to_currency")
        return redirect("/rates")

    def _update_rate(self, from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
        rates = CurrentRate.select()
        for rate in rates:
            try:
                self._update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                print(ex)


class Viewlogs(BaseController):
    def _call(self):
        page = int(self.request.args.get("page", 1))
        logs = ApiLog.select().paginate(page, 10).order_by(ApiLog.id.desc())
        return render_template("logs.html", logs=logs)


class EditRate(BaseController):
    def _call(self, from_currency, to_currency):

        if CurrentRate.select().where(CurrentRate.from_currency == from_currency,
                                      CurrentRate.to_currency == to_currency).first() is None:
            raise Exception("Rates not found")

        if self.request.method == "GET":
            return render_template("rate_edit.html", from_currency=from_currency, to_currency=to_currency)

        print(request.form)
        if "new_rate" not in request.form:
            raise Exception("new_rate parametr is required")

        if not request.form["new_rate"]:
            raise Exception("new_rate must be not empty")

        upd_count = (CurrentRate.update({CurrentRate.rate: float(request.form['new_rate']),
                                         CurrentRate.update_date: datetime.now()})
                     .where(CurrentRate.from_currency == from_currency,
                            CurrentRate.to_currency == to_currency)).execute()

        print("upd_count", upd_count)
        return redirect(url_for('view_rates'))
