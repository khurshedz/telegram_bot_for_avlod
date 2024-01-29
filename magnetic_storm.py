import requests
from datetime import datetime, timedelta

def get_magnetic_storm_level():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

    try:
        response = requests.get(url)
        data = response.json()

        if data:
            k_index = float(data[-1][1])
            k_index_str = str(k_index)
            last_update = convert_datetime(data[-1][0])

            if k_index < 4:
                k_index_str += '🟢'
            elif 4 <= k_index < 5:
                k_index_str += '🟡'
            elif 5 <= k_index < 6:
                k_index_str += '🔴'
            elif 6 <= k_index < 7:
                k_index_str += '🟣'

            storm_level = (
                f"Магнитный уровень {k_index_str}"
                f"\nПоследняя проверка {last_update}"
            )
            return storm_level

    except requests.exceptions.RequestException as e:
        return "Failed to retrieve data"

def convert_datetime(input_datetime):
    dt = datetime.strptime(input_datetime, '%Y-%m-%d %H:%M:%S.%f')
    new_dt = dt + timedelta(hours=3)
    return new_dt.strftime("%Y-%m-%d %H:%M")
