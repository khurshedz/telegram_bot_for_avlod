import requests

from custom_requests import get
from errors import IntegrationError
from secret import CURRENCY_KEY


def get_current_currency():
    try:
        response = get(f"https://openexchangerates.org/api/latest.json?app_id={CURRENCY_KEY}")
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise IntegrationError("Failed to retrieve currency data from OpenExchangeRates") from exc
    except ValueError as exc:
        raise IntegrationError("Failed to decode OpenExchangeRates response") from exc

    try:
        usd_tjs_rate = data["rates"]["TJS"]
        usd_rub_rate = data["rates"]["RUB"]
    except (KeyError, TypeError) as exc:
        raise IntegrationError("OpenExchangeRates response has unexpected format") from exc

    rub_tjs_rate = usd_tjs_rate / usd_rub_rate * 1000
    return usd_tjs_rate, usd_rub_rate, rub_tjs_rate


def get_exchange_rate():
    try:
        response = get('https://www.cbr-xml-daily.ru/daily_json.js')
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise IntegrationError("Failed to retrieve exchange rates from CBR") from exc
    except ValueError as exc:
        raise IntegrationError("Failed to decode CBR response") from exc

    try:
        usd_tjs_rate = data['Valute']['USD']['Value']
        usd_rub_rate = 10 / data['Valute']['TJS']['Value']
    except (KeyError, TypeError, ZeroDivisionError) as exc:
        raise IntegrationError("CBR response has unexpected format") from exc

    rub_tjs_rate = usd_rub_rate * usd_tjs_rate
    return rub_tjs_rate, usd_tjs_rate, usd_rub_rate * 1000


def get_needed_currency():
    try:
        usd, rub, tjs = get_current_currency()
    except IntegrationError:
        usd, rub, tjs = get_exchange_rate()

    return (
        f"1💲       : {usd:.2f} 🇹🇯\n"
        f"1💲       : {rub:.2f} 🇷🇺\n"
        f"1000 🇷🇺   : {tjs:.2f} 🇹🇯\n"
    )
