from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import TEXT_TO_PIC_FONT_PATH


def generate_image(text, output_path: str | Path = "text_image.png"):
    image = Image.new('RGBA', (150, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(TEXT_TO_PIC_FONT_PATH), 8)

    lines = text.split('\n')

    for i, line in enumerate(lines):
        draw.text((10, 10 + i * 20), line, font=font, fill=(0, 0, 0))

    image.save(Path(output_path))


text = """
Четверг 01.02.2024|14 дней
🔗 Лиды     1144|  -12%
👥 Рег.     1617|  -11%
🔑 Вход     2198| +122%
🛂 Идент.   1179|   -5%
💳 Карт     1213|   -5%
🆕 Создан   2067|   -5%
🚫 Отказ    1007|  -17%
❌ Отменён  499 |  -68%
✅ Одобрен  665 |   +4%
📥 Выдан    555 |   +7%
"""


generate_image(text)
