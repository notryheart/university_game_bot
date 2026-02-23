#Created by Antonov Yaroslav 23.02.2025

import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

TOKEN = "INSERT YOUR TOKEN"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = "CHOOSE YOUR ID"
#табличечка
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("SELECT YOUR KEY", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("YOUR GOOGLE SHEET LINK").sheet1

teams = ["Команда 1","Команда 2","Команда 3","Команда 4", "Команда 5","Команда 6","Команда 7","Команда 8"]

# функция проверки регистрации пользователя 
def is_registered(user_id):
    ids = sheet.col_values(1) #получаем список значений айдишек пользователей
    return str(user_id) in ids 

#функция сбора всех айди польхователей которая необходима для бродкаста
def get_all_users():
    ids = sheet.col_values(1)
    users = []
    for user_id in ids[1:]:
        if user_id:
            users.append(int(user_id)) #добавляем все айди в массив и возвращвем его
    return users

#прописываем коману сарта работы бота
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #меняем клаву на кнопки автоматически
    markup.add(types.KeyboardButton("Регистрация")) #рендерим кнопочки
    bot.send_message(message.chat.id, "Привет!\nНажми Регистрация", reply_markup=markup)

#прописываем команду для регистрации пользователя
@bot.message_handler(func = lambda message: message.text == "Регистрация")
def registration(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))
    bot.send_message(message.chat.id, "Выбери свою команду:", reply_markup=markup)

#прописываем команду для регистрации в команду
@bot.message_handler(func = lambda message: message.text in teams)
def choose_team(message):
    user = message.from_user

    if is_registered(user.id):
        bot.send_message(message.chat.id, "❌ Ты уже зарегистрирован!")
        return

    try: #юзаем трай для того, чтобы бот не отлетел к ебеням и не пришлось тратиться на дорогой хостинг с автоподключением
        sheet.append_row([user.id, user.username if user.username else "нет", user.first_name, message.text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        bot.send_message(message.chat.id, f"✅ Ты зарегистрирован в {message.text}!", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        bot.send_message(message.chat.id,"⚠️ Ошибка регистрации, попробуй через 5 секунд")
        print(e)
#прописываем команду отправки всем пользователям нашего бота
@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    msg = bot.send_message(message.chat.id, "✉️ Введи сообщение для рассылки:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    text = message.text
    sent = 0
    failed = 0
    for user_id in users:
        try:
            bot.send_message(user_id, text)
            sent += 1
        except:
            failed += 1
    bot.send_message(message.chat.id, f"✅ Рассылка завершена\n" f"Отправлено: {sent}\n" f"Не доставлено: {failed}")
#команда для добавления очков в команда (очень длинная и состоит из нескольких часей)
@bot.message_handler(commands=['addpoints'])
#первая фаза, состоящая из проверки на админа
def adding(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))
    msg = bot.send_message(message.chat.id, "Выбери команду:", reply_markup=markup)
    bot.register_next_step_handler(msg, select_team_for_points)
#вторая часть, непосредственно отвечающая за добавление определенного количества очков
def select_team_for_points(message):
    if message.text not in teams:
        return
    admin_data[message.from_user.id] = message.text
    msg = bot.send_message(message.chat.id, "Введи количество очков:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, enter_points_amount)
#добавление нашего значения в гугл таблицу + красиваое оформление вывода
def enter_points_amount(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text.isdigit():
        return
    points_to_add = int(message.text)
    team_name = admin_data.get(message.from_user.id)
    try:
        cell = sheet_2.find(team_name)
        row = cell.row
        current = sheet_2.cell(row, 2).value
        current_points = int(current) if current else 0
        new_points = current_points + points_to_add
        sheet_2.update_cell(row, 2, new_points)
        # оформление написал чат гпт
        bot.send_message(message.chat.id, f"Команда <b>{team_name}</b> получила <b>{points_to_add}</b> очков!\n" f"Теперь у неё: <b>{new_points}</b> очков", parse_mode="HTML")
    except Exception as e:
        print("ADD POINTS ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА")
# команда для вывода очков всех команд (доступна всем пользователям)
@bot.message_handler(commands=["info"])
def show_teams(message):
    try:
        points_and_teams = []
        for i in range(2, 10):
            row = sheet_2.row_values(i)
            if len(row) >= 2:
                team_name = row[0]
                points = int(row[1]) if row[1] else 0
                points_and_teams.append([team_name, points])
        points_and_teams.sort(key=lambda x: -x[1])
        #тут я использовал чат гпт, потому что в падлу оформлением заниматься
        medals = ["🥇", "🥈", "🥉"]
        text = "🏆 <b>Таблица лидеров</b>\n\n"
        for index, (team, points) in enumerate(points_and_teams):
            place = index + 1
            if index < 3:
                medal = medals[index]
                text += f"{medal} <b>{place} место</b> - {team} | {points} очков\n"
            else:
                text += f"{place} место - {team} | {points} очков\n"
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e: # кинул исключение, потому что в гугл апи предусмотрено конечное число запросов от пользователя
        print(e)
        bot.send_message(message.chat.id, "К огромному сожалению вы израсходовали количество запросов. пожалуйста повторите запрос через 30 секунд <3")


bot.polling(none_stop=True)
