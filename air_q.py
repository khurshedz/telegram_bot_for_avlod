from dataclasses import dataclass
from typing import Optional

from custom_requests import get
from secret import API_KEY_IQ_AIR

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


@dataclass(frozen=True)
class AirQualityDto:
    aqi: int
    temp: Optional[int]
    city: str
    source: str


class AirVisualProvider:
    source = 'airvisual'

    @staticmethod
    def _request_raw_data(lat: str, lon: str) -> Optional[dict]:
        url = f'http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={API_KEY_IQ_AIR}'
        response = get(url)
        data = response.json()
        status = data.get('status')
        if response.status_code != 200 or status == 'fail':
            return None
        return data

    def _parse(self, data: dict) -> AirQualityDto:
        current = data['data']['current']
        return AirQualityDto(
            aqi=current['pollution']['aqius'],
            temp=current['weather']['tp'],
            city=data['data']['city'],
            source=self.source,
        )

    def get_air_quality(self, lat: str, lon: str) -> Optional[AirQualityDto]:
        data = self._request_raw_data(lat, lon)
        if not data:
            return None
        return self._parse(data)


def format_air_quality(dto: AirQualityDto) -> str:
    city = TRANSLATED_CITY.get(dto.city, dto.city)
    air_quality_str = str(dto.aqi)

    if dto.aqi < 51:
        air_quality_str += '🟢'
    elif dto.aqi < 101:
        air_quality_str += '🟡'
    elif dto.aqi < 151:
        air_quality_str += '🟤'
    elif dto.aqi < 201:
        air_quality_str += '🔴'
    else:
        air_quality_str += '🟣'

    city = city.ljust(8)
    air_quality_str = air_quality_str.rjust(4)
    temperature = f'{dto.temp}°C'.ljust(4) if dto.temp is not None else 'n/a '

    return f"{city} — 💨:{air_quality_str}|🌡:{temperature}"


def get_air_quality() -> str:
    provider = AirVisualProvider()
    text = []

    for latlon in CITY.values():
        dto = provider.get_air_quality(*latlon)
        if dto:
            text.append(format_air_quality(dto))

    if text:
        return '\n'.join(text)
    return 'No air quality'
