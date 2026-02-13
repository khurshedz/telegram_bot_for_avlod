from datetime import datetime, timedelta

import requests

from custom_requests import get
from errors import IntegrationError


def get_magnetic_storm_level():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

    try:
        response = get(url, timeout=(5, 10))
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise IntegrationError("Failed to retrieve magnetic storm data") from exc
    except ValueError as exc:
        raise IntegrationError("Failed to decode magnetic storm response") from exc

    if not data:
        raise IntegrationError("Magnetic storm API returned empty data")

    try:
        k_index = float(data[-1][1])
        last_update = convert_datetime(data[-1][0])
    except (IndexError, TypeError, ValueError) as exc:
        raise IntegrationError("Magnetic storm data has unexpected format") from exc

    k_index_str = str(k_index)
    if k_index < 4:
        k_index_str += '🟢'
    elif 4 <= k_index < 5:
        k_index_str += '🟡'
    elif 5 <= k_index < 6:
        k_index_str += '🔴'
    elif 6 <= k_index < 15:
        k_index_str += '🟣'

    return (
        f"Магнитный уровень {k_index_str}"
        f"\nПоследняя проверка {last_update}"
    )


def convert_datetime(input_datetime):
    dt = datetime.strptime(input_datetime, '%Y-%m-%d %H:%M:%S.%f')
    new_dt = dt + timedelta(hours=3)
    return new_dt.strftime("%Y-%m-%d %H:%M")
