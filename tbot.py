import telebot
from telebot import types
import psycopg2
import datetime


token = "6155441710:AAHe_bz6tOVPY1vDTW7v4NjiGCvg2c0V9Kw"
zone = datetime.timezone(datetime.timedelta(hours=3))
bot = telebot.TeleBot(token)
conn = psycopg2.connect(database="laba_7",
                        user="postgres",
                        password="raul2004",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()


def find_parity():
	time = datetime.datetime.now(zone)
	if (int(time.strftime('%W')) - 34) % 2:
		return 'НЕЧЕТНАЯ'
	else:
		return 'ЧЕТНАЯ'


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('/help', '/week', '/mtuci', '/timetable')
    bot.send_message(message.chat.id, 'Привет! Хочешь узнать свежую информацию о МТУСИ?', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def give_information(message):
    bot.send_message(message.chat.id,   	'Бот с расписанием МТУСИ.\n'
                                            'Список комманд:\n'
                                            '/start - перезапуск бота\n'
                                            '/mtuci - ссылка на сайт МТУСИ\n'
                                            '/week - четность недели\n'
                                            '/timetable - расписание')

@bot.message_handler(commands=["mtuci"])
def give_a_website_link(message):
    bot.send_message(message.chat.id, '[Перейти на официальный сайт МТУСИ](https://mtuci.ru/)')

@bot.message_handler(commands=["week"])
def give_parity_of_the_week(message):
    p = find_parity()
    bot.send_message(message.chat.id, 'На данный момент ' + p + ' неделя')

@bot.message_handler(commands=['timetable'])
def show_timetable_keyboard(message):
	keyboard = types.ReplyKeyboardMarkup()
	keyboard.row('Понедельник', 'Вторник', 'Среда',
				'Четверг', 'Пятница', 'Суббота',
				'Расписание на текущую неделю', 'Расписание на следующую неделю')
	bot.send_message(message.chat.id, 'Выбери день или неделю', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def answer(message):

	if find_parity() == 'НЕЧЕТНАЯ':
		p = 'odd'
	else:
		p = 'even'

	if message.text.lower() == 'расписание на текущую неделю' or message.text.lower() =='расписание на следующую неделю':
		days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
		if message.text.lower() =='расписание на следующую неделю':
			if p == 'odd':
				p = 'even'
			else:
				p = 'odd'
		cursor.execute('''select e.day, e.subject, room_numb, e.start_time, t.full_name
							from {0}_week_timetable as e
							join subjects as s
								on e.subject = s.name
							join teachers as t
								on t.subject = s.name
							order by e.start_time;'''.format(p))
		elements = cursor.fetchall()
		m = ''
		for day in days:
			m += '\n' + day + '\n __________  \n'
			for el in elements:
				if day == el[0]:
					subject = el[1]
					room_numb = el[2]
					start_time = el[3]
					t_full_name = el[4]
					m += '\n{}, {}, {}, {} \n'.format(subject, room_numb, start_time, t_full_name)
			m += '\n __________\n'
		bot.send_message(message.chat.id, m)

	else:
		day = message.text.lower()
		cursor.execute('''select e.subject, e.room_numb, e.start_time, t.full_name
							from {0}_week_timetable as e
							join subjects as s
								on e.subject = s.name
							join teachers as t
								on t.subject = s.name
							where e.day = '{1}'
							order by e.start_time;'''.format(p, day))
		m = day + '\n __________  \n'
		for i in cursor.fetchall():
			subject = i[0]
			room_numb = i[1]
			start_time = i[2]
			t_full_name = i[3]
			m += '\n{}, {}, {}, {} \n'.format(subject, room_numb, start_time, t_full_name)
		m += '\n __________'
		bot.send_message(message.chat.id, m)

bot.polling(none_stop=True)

