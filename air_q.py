import requests

from secret import API_KEY_AQICN, API_KEY_IQ_AIR, API_KEY_WEATHER

CITY = {'Moscow': ['55.751244', '37.618423'],
        'Yekaterinburg': ['56.833332', '60.583332'],
        'Dushanbe': ['38.506497974', '68.224832434'],
        'Finland': ['62.24147', '25.72088']}


def request_weather(url):
    response = requests.get(url)
    data = response.json()
    status = data.get('status')
    if response.status_code != 200 or (status == 'fail'):
        return None
    return data


def get_air_quality():
    text = []
    for city, latlon in CITY.items():
        air_text = get_air_quality_iq_air(*latlon)
        text.append(air_text)
    return '\n'.join(text) if text else 'No air quality'


def get_air_quality_iq_air(lat, lon):
    url = f'http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={API_KEY_IQ_AIR}'
    data = request_weather(url)
    if not data:
        return None

    air_quality = data['data']['current']['pollution']['aqius']
    temperature = data['data']['current']['weather']['tp']
    city = data['data']['city']
    air_quality_str = str(air_quality)

    if 0 < air_quality < 51:
        air_quality_str += '🟢'
    elif 50 < air_quality < 101:
        air_quality_str += '🟡'
    elif 100 < air_quality < 151:
        air_quality_str += '🟤'
    elif 150 < air_quality < 201:
        air_quality_str += '🔴'
    elif air_quality > 200:
        air_quality_str += '🟣'

    city = city.ljust(13)
    air_quality_str = air_quality_str.rjust(3)
    temperature = f'{temperature}°C'.ljust(3)

    return f"{city} — 💨:{air_quality_str}|🌡:{temperature}"


def get_air_quality_weather(city):
    url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY_WEATHER}&q={city}&aqi=yes'
    data = request_weather(url)
    # Извлечение данных о качестве воздуха
    air_quality = data['current']

    # Вывод информации о качестве воздуха
    return city, air_quality


def get_air_quality_aqicn(city):
    url = f"http://api.waqi.info/feed/{city}/?token={API_KEY_AQICN}"
    data = request_weather(url)
    return data
