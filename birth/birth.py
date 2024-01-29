import csv
import datetime


class Birth:
    def __init__(self):
        self.text = ""
        self.path_to_pic = ""
        self.fio = ""

    def cheers_for_uli(self):
        self.fio = "Мустанов Улугбек"
        self.text = """
        
                  Вот и старше стал на год,
                  Старость скоро подойдет.
                  Очень скоро растолстеешь,
                  Поседеешь, полысеешь.
                
                  С днем рожденья поздравляю,
                  В жизни всё успеть желаю.
                  Пусть года хоть и идут,
                  Тебе счастье лишь несут!"""

        self.path_to_pic = 'pics/birth.jpg'

    def cheers_for_dosya(self):
        self.fio = "Рахмонов Достон"
        self.text = """
        
        С днем рождения поздравляю!
        Два кило любви желаю,
        Центнер новых впечатлений,
        Три вагона приключений!
        
        Чтоб заботились родные,
        Лишь объятия дарили,
        Замечательно жилось,
        А что надо — то сбылось!
        
        С каждым годом всё ближе пенсия. 
        Желаю встретить её со своими зубами,
        с морщинами только от смеха,
        в трезвом уме и при своей памяти!
        Пусть вопреки всему кальций не вымывается из костей,
        волосы не седеют, а нервные клетки восстанавливаются.
        Живи и молодей!
        """
        self.path_to_pic = 'pics/dosya.jpeg'

    def get_current_text_pic(self):
        self.add_fio()
        return self.text, self.path_to_pic

    def add_fio(self):
        self.text = f"Поздравляем {self.fio} с днём рождения! Аз гурухи Авлод поздравление \n {self.text}"



# def add_birthday(name, birthday):
#     with open('birthdays.csv', 'a', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow([name, birthday, 'False'])

#add_birthday('Мустанов Улугбек', '2001-29-01')

def send_birthday_notification(name):
    print(f"С днем рождения, {name}! Желаю вам прекрасного дня!")
    # Обновление поля is_congratulated в CSV файле
    with open('db/birthdays.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
    with open('db/birthdays.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            if row[0] == name:
                row[2] = 'True'
            writer.writerow(row)


def check_birthdays():
    today = datetime.date.today()
    with open('db/birthdays.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Пропустить заголовок
        for row in reader:
            birthday = datetime.datetime.strptime(row[1], '%Y-%m-%d').date()
            if today.day == birthday.day and today.month == birthday.month and row[2] == 'False':
                send_birthday_notification(row[0])


check_birthdays()
