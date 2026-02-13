from custom_requests import get
from secret import API_KEY_AQICN, API_KEY_IQ_AIR, API_KEY_WEATHER

CITY = {
    'Moscow': ['55.751244', '37.618423'],
    'Saint-Petersburg': ['60.062729', '30.307619'],
    'Yekaterinburg': ['56.833332', '60.583332'],
    'Dushanbe': ['38.53575', '68.77905'],
    'Denov': ['38.506497974', '68.224832434'],
}

TRANSLATED_CITY = {
    'Moscow': 'Мск',
    'Yekaterinburg': 'Екб',
    'Denov': 'Деноу',
    'Dushanbe': 'Душанбе',
    'Akademicheskoe': 'СпБ',
}


def request_weather(url):
    response = get(url)
    data = response.json()
    status = data.get('status')
    if response.status_code != 200 or (status == 'fail'):
        return None
    return data


def get_air_quality():
    text = []
    for latlon in CITY.values():
        air_text = get_air_quality_iq_air(*latlon)
        text.append(air_text)

    if text:
        return '\n'.join(text)
    else:
        return 'No air quality'


def get_air_quality_iq_air(lat, lon):
    url = f'http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={API_KEY_IQ_AIR}'
    data = request_weather(url)
    if not data:
        return None

    air_quality = data['data']['current']['pollution']['aqius']
    temperature = data['data']['current']['weather']['tp']
    city = TRANSLATED_CITY.get(data['data']['city'])
    air_quality_str = str(air_quality)

    if air_quality < 51:
        air_quality_str += '🟢'
    elif 50 < air_quality < 101:
        air_quality_str += '🟡'
    elif 100 < air_quality < 151:
        air_quality_str += '🟤'
    elif 150 < air_quality < 201:
        air_quality_str += '🔴'
    elif air_quality > 200:
        air_quality_str += '🟣'

    city = city.ljust(8)
    air_quality_str = air_quality_str.rjust(4)
    temperature = f'{temperature}°C'.ljust(4)

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
