from PIL import Image, ImageDraw, ImageFont


def generate_image(text):
    # Создание изображения
    image = Image.new('RGBA', (150, 300), color=(255, 255, 255))

    # Создание объекта для рисования
    draw = ImageDraw.Draw(image)

    # Загрузка шрифта
    font = ImageFont.truetype("/home/spac/git/finance-world/auxiliary_files/_repositories/src/git-new.dengabank.ru/backend/finance/fonts/arial.ttf", 8)

    # Разбиение текста на строки
    lines = text.split('\n')

    # Отрисовка каждой строки текста
    for i, line in enumerate(lines):
        draw.text((10, 10 + i * 20), line, font=font, fill=(0, 0, 0))

    image.save("text_image.png")


# Ваш текст
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

# Генерация изображения
generate_image(text)


