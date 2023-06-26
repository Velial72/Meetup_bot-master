import os
import sqlite3
import requests
from datetime import datetime
import time
import telebot
from telebot import types
from dotenv import load_dotenv
from pathlib import Path

from django.core.management.base import BaseCommand


load_dotenv()
token = '6125022357:AAHc-FiPd5qsIyHhKaAiTKIft-1h1Jq34HU'
bot = telebot.TeleBot(token)
path = Path("meetup", "db.meetup")
conn = sqlite3.connect(path, check_same_thread=False)
cursor = conn.cursor()
params = []
questions = []
author_of_quastion = []
speaker_name = ''


def now_time(): # выдает текущий час
    current_time = datetime.now().hour
    return current_time


def get_speakers_list(): #выводит список спикеров
    cursor.execute(f"SELECT user_id FROM bot_speaker")
    speakers_name = cursor.fetchall()

    return speakers_name


def get_timeline(): # выдает боту график мероприятия
    cursor.execute("SELECT * FROM bot_speaker;")
    i = cursor.fetchall()
    return i


def check_meet(speaker_id): #проверяет задержку выступления
    cursor.execute(f"SELECT id FROM bot_user WHERE tg_id == '{speaker_id}'")
    name = cursor.fetchone()
    cursor.execute(f"SELECT delay FROM bot_speaker WHERE user_id == '{name[0]}'")
    return cursor.fetchone()[0]



def get_name(message): # получить данные спикера
    speaker_id = message.from_user.id
    return check_meet(speaker_id)


def get_name_visitor(message): # получить данные пользователя
    visitor_name = message.from_user.first_name
    visitor_id = message.from_user.id
    params.append(visitor_id)
    params.append(visitor_name)
    check_user(visitor_id)


def check_user(tg_id): # проверяет записан ли пользователь
    cursor.execute(f"SELECT tg_id FROM bot_user WHERE tg_id == {tg_id}")
    data = cursor.fetchone()
    if data is None:
        add_user(tg_id=params[0], name=params[1])


def find_speaker(): # находит имя спикера по времени
    cursor.execute(f"SELECT user_id FROM bot_speaker WHERE start_date == '{now_time()}:00';")
    name_of_speaker = cursor.fetchone()
    return name_of_speaker[0]


def get_question(message): # получает вопрос от пользователя
    question = message.text
    name_visitor = message.from_user.id
    questions.append(question)
    author_of_quastion.append(name_visitor)
    send_question(guest=name_visitor, speaker=find_speaker(), message=questions)


def add_user(tg_id: str, name: str): # добавить пользователя в БД
    cursor.execute('INSERT INTO bot_user(tg_id, name) VALUES (?,?)',
                   (params[0], params[1]))
    conn.commit()


def get_my_questions(): # выводит вопросы спикеру
    cursor.execute(f"SELECT * FROM bot_message WHERE speaker_id == '{find_speaker()}';")
    return cursor.fetchall()


def send_question(guest: str, speaker: str, message: str): # добавляет вопрос в БД
    cursor.execute('INSERT INTO bot_message(guest_id, speaker_id, message) VALUES (?,?,?)',
                   (author_of_quastion[-1], find_speaker(), questions[-1]))
    conn.commit()

def get_users():
    cursor.execute(f"SELECT tg_id FROM bot_user;")
    tg_id = cursor.fetchall()
    return tg_id

def start_meetup(message):
    meet = message.text
    cursor.execute(f"SELECT delay FROM bot_speaker WHERE id = '{int(meet)}';")
    delay = cursor.fetchone()
    print(type(delay[0]))
    if delay[0] == 0:
        cursor.execute(f"UPDATE bot_speaker SET delay = '1' WHERE id = '{meet}';")
        conn.commit()
    else:
        cursor.execute(f"UPDATE bot_speaker SET delay = '0' WHERE id = '{meet}'")
        conn.commit()


# def mailing():
#     cursor.execute(f"SELECT message FROM bot_message;")
#     message = cursor.fetchall()
#     return message

@bot.message_handler(content_types=['text']) # Пришли сообщение чтобы начать
def start(message):
    if message.from_user.username == 'AbRamS0404': #Konstantin_Derienko
        markup = types.InlineKeyboardMarkup(row_width=1)
        timeline = types.InlineKeyboardButton('График выступлений', callback_data='timeline')
        timeline2 = types.InlineKeyboardButton('Управлять выступлениями', callback_data='timeline2')
        send_message = types.InlineKeyboardButton('Оповестить об изменениях', callback_data='send')
        #mailing = types.InlineKeyboardButton('Отправить сообщение', callback_data='mailing')
        markup.add(timeline, timeline2, send_message)
        bot.send_message(message.chat.id, '\nпосмотрим расписание?\n', reply_markup=markup)

    elif get_name(message) == 1: # добавить сравнение времени спикера и текущего времени
        markup = types.InlineKeyboardMarkup(row_width=1)
        questions = types.InlineKeyboardButton('Вопросы слушателей', callback_data='questions')
        timeline = types.InlineKeyboardButton('График выступлений', callback_data='timeline')
        ask_question = types.InlineKeyboardButton('Задать вопрос', callback_data='ask_question')
        about_bot = types.InlineKeyboardButton('Что я могу', callback_data='about')
        markup.add(questions, timeline, ask_question, about_bot)

        bot.send_message(message.chat.id, '\nвыбери нужный пункт', reply_markup=markup)

    else:
        markup=types.InlineKeyboardMarkup(row_width=1)
        timeline=types.InlineKeyboardButton('График выступлений', callback_data='timeline')
        ask_question=types.InlineKeyboardButton('Задать вопрос', callback_data='ask_question')
        about_bot=types.InlineKeyboardButton('Что я могу', callback_data='about')
        markup.add(timeline, ask_question, about_bot)
        bot.send_message(message.chat.id, '\nвыбери нужный пункт', reply_markup=markup)
        get_name_visitor(message)


@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.data == 'about': # готово
        text = 'Я расскажу какие ожидаются выступления, а еще через меня можно задать вопрос спикеру!\n\n для возврата домой отправь мне сообщение\n'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                text=f'\n{text}',
                                parse_mode='Markdown')

    elif call.data == 'timeline': # Готово
        for number, meet in enumerate(get_timeline()):
            start_time = meet[1]
            end_time = meet[2]
            meet_theme = meet[3]
            if number == 0:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\nс {start_time} до {end_time}\nтема: {meet_theme}')
                time.sleep(0.5)
            elif number == len(get_timeline())-1:
                bot.send_message(call.message.chat.id,
                                 text=f'\nс {start_time} до {end_time}\nтема: {meet_theme}')
                time.sleep(0.5)
            else:
                bot.send_message(call.message.chat.id, text=f'\nс {start_time} до {end_time}\nтема: {meet_theme}')
                time.sleep(0.5)
        bot.send_message(call.message.chat.id,
                         text=f'\n\nдля возврата домой отправь мне сообщение')

    elif call.data == 'timeline2': # Готово
        for number, meet in enumerate(get_timeline()):
            print(meet)
            in_process = 'не идет'
            if meet[4] == 1:
                in_process = 'идет'
            number_of_meet = meet[0]
            start_time = meet[1]
            end_time = meet[2]
            meet_theme = meet[3]
            if number == 0:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f'\n{number_of_meet} с {start_time} до {end_time} \nтема: {meet_theme}\n\nВыступление {in_process}')
                time.sleep(0.5)

            else:
                bot.send_message(call.message.chat.id, text=f'\n{number_of_meet} с {start_time} до {end_time} \nтема: {meet_theme}\n\nВыступление {in_process}')
                time.sleep(0.5)

        markup = types.InlineKeyboardMarkup(row_width=2)
        start = types.InlineKeyboardButton('Начал', callback_data='start')
        finish = types.InlineKeyboardButton('Закончил', callback_data='finish')
        markup.add(start, finish)
        sent = bot.send_message(call.message.chat.id, text='\nотправь номер мероприятия и нажми "началось" или "закончилось"', reply_markup=markup)
        bot.register_next_step_handler(sent, start_meetup)

    elif call.data == 'start':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='\nвыступление началось\n\n для возврата домой отправь мне сообщение\n')

    elif call.data == 'finish':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='\nвыступление закончилось\n\n для возврата домой отправь мне сообщение\n')

    elif call.data == 'ask_question': # готово
        markup = types.InlineKeyboardMarkup(row_width=2)

        ask = types.InlineKeyboardButton('Спросить', callback_data='ask')
        markup.add(ask)
        sent = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                     text='\nЗадай свой вопрос\n\n', reply_markup=markup)
        bot.register_next_step_handler(sent, get_question)

    elif call.data == 'ask': # готово
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='\nСпасибо за вопрос\n\n для возврата домой отправь мне сообщение\n')

    elif call.data == 'questions': ### будет брать вопросы из БД для конкретного спикера? НЕ УДАЛЯЕТ ПРИ ОБНОВЛЕНИИ
        markup = types.InlineKeyboardMarkup(row_width=2)
        update = types.InlineKeyboardButton('Обновить', callback_data='questions')
        markup.add(update)
        for number, question in enumerate(get_my_questions()):
            print(question)
            visitor_question = question[1]
            if number == len(get_my_questions())-1:
                bot.send_message(call.message.chat.id, text=f'\nВопрос от слушателя:\n{visitor_question}\n\n для возврата домой отправь мне сообщение\n', reply_markup=markup)
                time.sleep(0.5)
            else:
                bot.send_message(call.message.chat.id, text=f'\nВопрос от слушателя:\n{visitor_question}\n\n')
                time.sleep(0.5)

    elif call.data == 'send':
        for user in get_users():
            print(user)
            params = {
                'chat_id': user[0],
                'text': 'График мероприятий изменен',
            }
            response = requests.get('https://api.telegram.org/bot'+token+'/sendMessage', params=params)

    elif call.data == 'mailing':
        for user in get_users():
            params = {
                'chat_id': user[0],
                'text': mailing(),
            }
            response = requests.get('https://api.telegram.org/bot'+token+'/sendMessage', params=params)


    # elif call.data == 'home':
    #     bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    #     start(call.message)


class Command(BaseCommand):
    help = 'телеграм бот собраний'

    def handle(self, *args, **options):
        # print(bot.get_me())
        while True:
            try:
                bot.polling(none_stop=True)
            except Exception as error:
                print(error)
                time.sleep(5)
