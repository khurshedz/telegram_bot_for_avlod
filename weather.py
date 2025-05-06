import abc
import requests
import json
from typing import Tuple, Optional
from secret import AV_API_KEY, OWM_API_KEY
from custom_requests import get

def make_request(url: str) -> Optional[dict]:
    try:
        response = get(url)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.exceptions.RequestException:
        return None


class BaseAQIProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def _fetch_raw_data(self, lat, lon) -> dict:
        pass

    @property
    @abc.abstractmethod
    def api_key(self) -> str:
        pass

    def get_aqi(self, lat, lon) -> Tuple[int, Optional[float]]:
        raw_data = self._fetch_raw_data(lat, lon)
        aqi = self._parse_aqi(raw_data)
        temp = self._parse_temperature(raw_data)
        return aqi, temp


class BaseWeatherProvider(BaseAQIProvider):
    @abc.abstractmethod
    def _parse_description(self, raw_data: dict) -> str:
        pass

    def get_weather_info(self, lat, lon) -> Tuple[str, int, Optional[float]]:
        raw_data = self._fetch_raw_data(lat, lon)
        description = self._parse_description(raw_data)
        aqi, temperature = super().get_aqi(lat, lon)
        return description, aqi, temperature


class AirVisualApi(BaseAQIProvider):
    @staticmethod
    def _fetch_raw_data(lat, lon) -> dict:
        url = f"http://api.airvisual.com/v2/nearest_city?key={AV_API_KEY}&lat={lat}&lon={lon}"
        response = get(url)
        return json.loads(response.content)

    @property
    def api_key(self) -> str:
        return AV_API_KEY

    def _parse_aqi(self, raw_data: dict) -> int:
        return raw_data['data']['current']['pollution']['aqius']

    def _parse_temperature(self, raw_data: dict) -> Optional[float]:
        return None


class OpenWeatherMapApi(BaseWeatherProvider):
    @staticmethod
    def _fetch_raw_data(lat, lon) -> dict:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}"
        response = get(url)
        return json.loads(response.content)

    @property
    def api_key(self) -> str:
        return OWM_API_KEY

    def _parse_aqi(self, raw_data: dict) -> Optional[int]:
        return None

    def _parse_temperature(self, raw_data: dict) -> Optional[float]:
        if "main" in raw_data and "temp" in raw_data["main"]:
            return round(float(raw_data["main"]["temp"]) - 273.15, 2)
        else:
            return None

    def _parse_description(self, raw_data: dict) -> str:
        if "weather" in raw_data and len(raw_data["weather"]) > 0:
            return raw_data['weather'][0]['description']
        else:
            return "Weather description not available"


if __name__ == "__main__":
    av_provider = AirVisualApi()
    owm_provider = OpenWeatherMapApi()

    lat = 40.7128
    lon = -74.0060

    aqi, temp = av_provider.get_aqi(lat, lon)
    print(f"Air Visual AQI: {aqi}, Temperature: {temp}")

    desc, aqi, temp = owm_provider.get_weather_info(lat, lon)
    print(f"Open Weather Map Description: {desc}, AQI: {aqi}, Temperature: {temp}")
