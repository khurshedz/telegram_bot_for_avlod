import requests
from custom_requests import get

from secret import CURRENCY_KEY


def get_current_currency():
    response = get(f"https://openexchangerates.org/api/latest.json?app_id={CURRENCY_KEY}")
    if response.status_code != 200:
        return None

    data = response.json()
    usd_rate = data["rates"]["TJS"]
    rub_rate = data["rates"]["RUB"]
    tjs_rate = usd_rate / rub_rate * 1000
    return usd_rate, rub_rate, tjs_rate


def get_exchange_rate():
    try:
        response = get('https://www.cbr-xml-daily.ru/daily_json.js')
        data = response.json()
        usd_rate = data['Valute']['USD']['Value']
        rub_rate = 10 / data['Valute']['TJS']['Value']
        tjs_rate = rub_rate * usd_rate
        return usd_rate, rub_rate * 1000, tjs_rate
    except requests.exceptions.RequestException:
        return None


def get_needed_currency():
    current = get_current_currency()
    if current is None:
        current = get_exchange_rate()

    if current is None:
        return "Не удалось получить курсы валют ни из основного, ни из резервного источника."

    usd, rub, tjs = current
    return (
        f"1💲       : {usd:.2f} 🇹🇯\n"
        f"1💲       : {rub:.2f} 🇷🇺\n"
        f"1000 🇷🇺   : {tjs:.2f} 🇹🇯\n"
    )

