import csv
import datetime
import os
import random
from config import CSV_FILE_NAME, TEXT_FILE_NAME, PIC_FILDER_NAME


class BirthdayReminder:
    def __init__(self):
        self.csv_file = CSV_FILE_NAME
        self.text_file = TEXT_FILE_NAME
        self.pic_folder = PIC_FILDER_NAME
        self.text = ''
        self.name = ''

    def send_birthday_notification(self):
        self.update_congratulated_status()
        return (f"Поздравляем {self.name} с днём рождения! "
                f"Аз гурухи Авлод поздравление \n \n {self.text}",
                self.get_random_file())

    def update_congratulated_status(self):
        with open(self.csv_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader if row[0] != self.name]

        rows.append([self.name, datetime.datetime.now().strftime('%Y-%m-%d'), 'True'])

        with open(self.csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

    def check_birthdays(self):
        today = datetime.date.today()

        with open(self.csv_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)

            for row in reader:
                birthday = datetime.datetime.strptime(row[1], '%Y-%m-%d').date()

                if (today.day, today.month) == (birthday.day, birthday.month):
                    self.name = row[0]
                    self.text = self.get_random_text()
                    return self.send_birthday_notification()

    @staticmethod
    def split_text_into_lines(text):
        words = text.split()
        lines = [' '.join(words[i:i + 4]) for i in range(0, len(words), 4)]

        return '\n'.join(lines)

    def get_random_text(self):
        with open(self.text_file, 'r') as file:
            lines = file.readlines()

        random_line = random.choice(lines)
        return self.split_text_into_lines(random_line)

    def get_random_file(self, random_pic_folder=None):
        pic_folder = random_pic_folder or self.pic_folder
        folder = os.path.join(os.getcwd(), pic_folder)

        files = os.listdir(pic_folder)
        random_file = random.choice(files)

        return os.path.join(folder, random_file)

