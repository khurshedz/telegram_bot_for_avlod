import requests

from secret import TOKEN


def send_message(chat_id, text='Не работает =(', parse_mode='HTML'):
    URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    response = requests.post(URL, data=payload)
    return response.json()


def send_photo(chat_id, photo, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    files = {}
    if isinstance(photo, str):
        files['photo'] = open(photo, 'rb')
    else:
        files['photo'] = photo.read()

    data = {'chat_id': chat_id, 'caption': text, 'parse_mode': 'HTML'}
    response = requests.post(url, files=files, data=data)
    return response.json()


# def align_text(text, key_separator=":"):
#     aligned_lines = []
#     for line in text.split("\n"):
#         if key_separator in line:
#             key, value = map(str.strip, line.split(key_separator, 1))
#             aligned_lines.append(f"{key:<10}{value}".rjust(4))
#         else:
#             aligned_lines.append(line.strip().ljust(4))
#     return "\n".join(aligned_lines)
#
