import csv
import datetime
import random
import os


class BirthdayReminder:
    def __init__(self):
        self.csv_file = '/home/spac/PycharmProjects/telegram_bot/birth/db/birthdays.csv'
        self.text_file = '/home/spac/PycharmProjects/telegram_bot/birth/db/random_text.txt'
        self.pic_folder = '/home/spac/PycharmProjects/telegram_bot/birth/pics/'
        self.text = ''
        self.name = ''

    def send_birthday_notification(self):
        self.update_congratulated_status()

        return (f"Поздравляем {self.name} с днём рождения! Аз гурухи Авлод поздравление \n {self.text}"
                , self.get_random_file())

    def update_congratulated_status(self):
        # для чтения
        with open(self.csv_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            for row in rows:
                if row[0] == self.name:
                    row[2] = 'True'  # пишем в список

        # для записи в базу
        with open(self.csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)

    def check_birthdays(self):
        today = datetime.date.today()
        print(self.csv_file, self.text_file)
        with open(self.csv_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропустить заголовок
            try:
                for row in reader:
                    birthday = datetime.datetime.strptime(row[1], '%Y-%m-%d').date()
                    if today.day == birthday.day and today.month == birthday.month and row[2] == 'False':
                        self.name = row[0]
                        self.text = self.get_random_text()
                        return self.send_birthday_notification()
            except BaseException as e:
                print(e)

    @staticmethod
    def split_text_into_lines(text):
        words = text.split()
        lines = []
        for i in range(0, len(words), 4):
            line = ' '.join(words[i:i+4])
            lines.append(line)
        return '\n'.join(lines)

    def get_random_text(self):
        with open(self.text_file, 'r') as file:
            lines = file.readlines()
            random_line = random.choice(lines)
            formatted_text = self.split_text_into_lines(random_line)
            return formatted_text

    def get_random_file(self):
        folder = os.path.join(os.getcwd(), self.pic_folder)
        files = os.listdir(self.pic_folder)
        random_file = random.choice(files)
        random_file_path = os.path.join(folder, random_file)
        return random_file_path