import requests
from custom_requests import get

from secret import CURRENCY_KEY


def get_current_currency():
    response = get(f"https://openexchangerates.org/api/latest.json?app_id={CURRENCY_KEY}")
    if response.status_code != 200:
        return None

    data = response.json()
    usd_tjs_rate = data["rates"]["TJS"]
    usd_rub_rate = data["rates"]["RUB"]
    rub_tjs_rate = usd_tjs_rate / usd_rub_rate * 1000
    return usd_tjs_rate, usd_rub_rate, rub_tjs_rate


def get_exchange_rate():
    try:
        response = get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_tjs_rate = data['Valute']['USD']['Value']
        usd_rub_rate = 10 / data['Valute']['TJS']['Value']
        rub_tjs_rate = usd_rub_rate * usd_tjs_rate
        return rub_tjs_rate, usd_tjs_rate, usd_rub_rate * 1000
    except requests.exceptions.RequestException as e:
        return None


def get_needed_currency():
    data = get_current_currency() if get_current_currency() else get_exchange_rate()
    usd, tjs, rub = data
    return (
        f"1💲       : {usd:.2f} 🇹🇯\n"
        f"1💲       : {tjs:.2f} 🇷🇺\n"
        f"1000 🇷🇺   : {rub:.2f} 🇹🇯\n"
    )


