import abc
import json
from typing import Optional, Tuple

import requests
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
    def _fetch_raw_data(self, lat: float, lon: float) -> Optional[dict]:
        pass

    @abc.abstractmethod
    def _parse_aqi(self, raw_data: Optional[dict]) -> Optional[int]:
        pass

    @abc.abstractmethod
    def _parse_temperature(self, raw_data: Optional[dict]) -> Optional[float]:
        pass

    @property
    @abc.abstractmethod
    def api_key(self) -> str:
        pass

    def parse_metrics(self, raw_data: Optional[dict]) -> Tuple[Optional[int], Optional[float]]:
        aqi = self._parse_aqi(raw_data)
        temp = self._parse_temperature(raw_data)
        return aqi, temp

    def get_aqi(self, lat: float, lon: float) -> Tuple[Optional[int], Optional[float]]:
        raw_data = self._fetch_raw_data(lat, lon)
        return self.parse_metrics(raw_data)


class BaseWeatherProvider(BaseAQIProvider):
    @abc.abstractmethod
    def _parse_description(self, raw_data: Optional[dict]) -> str:
        pass

    def get_weather_info(self, lat: float, lon: float) -> Tuple[str, Optional[int], Optional[float]]:
        raw_data = self._fetch_raw_data(lat, lon)
        description = self._parse_description(raw_data)
        aqi, temperature = self.parse_metrics(raw_data)
        return description, aqi, temperature


class AirVisualApi(BaseAQIProvider):
    @staticmethod
    def _fetch_raw_data(lat: float, lon: float) -> Optional[dict]:
        url = f"http://api.airvisual.com/v2/nearest_city?key={AV_API_KEY}&lat={lat}&lon={lon}"
        try:
            response = get(url)
            response.raise_for_status()
            return json.loads(response.content)
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return None

    @property
    def api_key(self) -> str:
        return AV_API_KEY

    def _parse_aqi(self, raw_data: Optional[dict]) -> Optional[int]:
        try:
            return int(raw_data['data']['current']['pollution']['aqius'])
        except (TypeError, KeyError, ValueError):
            return None

    def _parse_temperature(self, raw_data: Optional[dict]) -> Optional[float]:
        return None


class OpenWeatherMapApi(BaseWeatherProvider):
    @staticmethod
    def _fetch_raw_data(lat: float, lon: float) -> Optional[dict]:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OWM_API_KEY}"
        try:
            response = get(url)
            response.raise_for_status()
            return json.loads(response.content)
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return None

    @property
    def api_key(self) -> str:
        return OWM_API_KEY

    def _parse_aqi(self, raw_data: Optional[dict]) -> Optional[int]:
        return None

    def _parse_temperature(self, raw_data: Optional[dict]) -> Optional[float]:
        try:
            return round(float(raw_data["main"]["temp"]) - 273.15, 2)
        except (TypeError, KeyError, ValueError):
            return None

    def _parse_description(self, raw_data: Optional[dict]) -> str:
        try:
            return raw_data['weather'][0]['description']
        except (TypeError, KeyError, IndexError):
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
