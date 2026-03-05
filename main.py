import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =========================
# Настройки Telegram-бота
# =========================
TOKEN = "8019982514:AAFGVa5iPpp__gmh7ksvS43zrJhmYIy3PMU"  # ⚠️ лучше хранить вне кода
bot = telebot.TeleBot(TOKEN)

# ID админа (имеет доступ к /check /broadcast /addpoints)
ADMIN_ID = 6601944801

# Словари для хранения временных состояний
admin_mode = {}      # сейчас почти не используется (есть остатки логики)
admin_data = {}      # для админ-сценариев (/addpoints, /check)
user_sessions = {}   # для сценария "заражение"

# ASUKA IS GOOD BUT KAWORU DEFINITELY BETTER


# =========================
# Подключение к Google Sheets
# =========================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Авторизация сервис-аккаунтом (json)
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "telegram_bot/telegrambotproject-488220-a7fc4e6fa52d.json",
    scope
)
client = gspread.authorize(creds)

# Таблица регистрации пользователей
sheet = client.open_by_key("1T6-e0zrmZKHkJ6v3xv_vq0i7hd3jT6K0Cifd4Svy2Zk").sheet1

# Таблица команд: очки (col2) и жизни (col3)
sheet_2 = client.open_by_key("12_WiTULAvKVcPXOP4bda7FSR3DUGHVHmM2ZEYme418w").sheet1

# Таблица чекпоинтов (посещения)
sheet_3 = client.open_by_key("1kwTDIUrNnpK6xfyktCBORsoG4RPw4ofdKnhTtz4pTfQ").sheet1

# Список команд — используется в меню и логике
teams = ["Команда 1", "Команда 2", "Команда 3", "Команда 4",
         "Команда 5", "Команда 6", "Команда 7", "Команда 8"]


# =========================
# Функции регистрации/пользователей
# =========================
def is_registered(user_id):
    # Берём колонку ID (1-я колонка), проверяем, есть ли user_id
    ids = sheet.col_values(1)
    return str(user_id) in ids


def get_all_users():
    # Собираем всех зарегистрированных user_id (для рассылки)
    ids = sheet.col_values(1)
    users = []
    for user_id in ids[1:]:  # пропускаем заголовок
        if user_id:
            users.append(int(user_id))
    return users


# =========================
# Главное меню (клавиатура)
# =========================
def buttons(message):
    # Создаём Reply-клавиатуру (кнопки)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Регистрация"))
    markup.add(types.KeyboardButton("Правила"))
    markup.add(types.KeyboardButton("Персонажи"))
    markup.add(types.KeyboardButton("Статистика"))
    markup.add(types.KeyboardButton("Потратить очки заражения"))

    # Для админа просто другой текст, кнопки те же
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Меню (админ): /check, /broadcast, /addpoints",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Меню:",
            reply_markup=markup
        )


# =========================
# /start — запуск бота
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    # Здесь ты вручную повторяешь меню (аналог buttons), чтобы сразу показать кнопки
    if message.from_user.id != ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Регистрация"))
        markup.add(types.KeyboardButton("Правила"))
        markup.add(types.KeyboardButton("Персонажи"))
        markup.add(types.KeyboardButton("Статистика"))
        markup.add(types.KeyboardButton("Потратить очки заражения"))
        bot.send_message(message.chat.id, "Привет!", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Регистрация"))
    markup.add(types.KeyboardButton("Правила"))
    markup.add(types.KeyboardButton("Персонажи"))
    markup.add(types.KeyboardButton("Статистика"))
    markup.add(types.KeyboardButton("Потратить очки заражения"))
    bot.send_message(
        message.chat.id,
        "Привет! Команды админа: /check, /broadcast, /addpoints",
        reply_markup=markup
    )


# =========================
# Регистрация (кнопка)
# =========================
@bot.message_handler(func=lambda message: message.text == "Регистрация")
def registration(message):
    # Показываем список команд кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))
    bot.send_message(message.chat.id, "Выбери свою команду:", reply_markup=markup)


# =========================
# Персонажи (словарь + обработчики)
# =========================
characters = {
    "Сергей Королёв": (
        "🚀 <b>Сергей Королёв</b>\n"
        "Главный конструктор. Твоя суперсила — превращать хаос в систему.\n"
        "Пассивка: +1 к воле команды, когда всё горит.\n\n"
    ),
    "Андрей Туполев": (
        "✈️ <b>Андрей Туполев</b>\n"
        "Авиаконструктор. Твоя суперсила — надёжность и расчёт.\n"
        "Пассивка: шанс избежать критической ошибки в проекте.\n\n"
    ),
    "Владимир Шухов": (
        "🧠 <b>Владимир Шухов</b>\n"
        "Инженер-новатор. Твоя суперсила — гениальная простота.\n"
        "Пассивка: находишь решение там, где другие видят тупик.\n\n"
    ),
    "Николай Жуковский": (
        "🌬️ <b>Николай Жуковский</b>\n"
        "Основоположник аэродинамики. Твоя суперсила — теория, которая работает.\n"
        "Пассивка: +точность в расчётах и планировании.\n\n"
    ),
    "Игорь Сикорский": (
        "🚁 <b>Игорь Сикорский</b>\n"
        "Пионер авиации. Твоя суперсила — смелые идеи.\n"
        "Пассивка: ускоряешь прогресс команды, но риск выше.\n\n"
    ),
}

@bot.message_handler(func=lambda message: message.text == "Персонажи")
def characters_listing(message):
    # Показываем кнопки персонажей + "В меню"
    if not characters:
        bot.send_message(message.chat.id, "Персонажи пока не добавлены.")
        buttons(message)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in characters.keys():
        markup.add(types.KeyboardButton(name))
    markup.add(types.KeyboardButton("В меню"))
    bot.send_message(message.chat.id, "Выбери персонажа:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in list(characters.keys()) + ["В меню"])
def send_character_info(message):
    # Если нажали "В меню" — возвращаем клавиатуру
    if message.text == "В меню":
        buttons(message)
        return

    # Иначе отправляем описание выбранного персонажа
    bot.send_message(message.chat.id, characters[message.text], parse_mode="HTML")
    buttons(message)


# =========================
# Выбор команды для регистрации (когда нажали "Команда N")
# =========================
@bot.message_handler(func=lambda message: message.text in teams)
def choose_team(message):
    # ⚠️ Тут есть кусок старой логики — choose_team_to_add_points не определена.
    # Сейчас admin_mode нигде не ставится в "adding_points", так что обычно не сработает.
    if admin_mode.get(message.from_user.id) == "adding_points":
        choose_team_to_add_points(message)  # ⚠️ этой функции нет — если вызовется, бот упадёт
        return

    user = message.from_user

    # Если пользователь уже в таблице регистрации — говорим об этом
    if is_registered(user.id):
        bot.send_message(message.chat.id, "Ты уже зарегистрирован!", reply_markup=types.ReplyKeyboardRemove())
        buttons(message)
        return

    try:
        # Записываем данные в sheet регистрации:
        # [id, username/нет, first_name, команда, timestamp]
        sheet.append_row([
            user.id,
            user.username if user.username else "нет",
            user.first_name,
            message.text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

        bot.send_message(message.chat.id, f"✅ Ты зарегистрирован в {message.text}!", reply_markup=types.ReplyKeyboardRemove())
        buttons(message)

    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ошибка регистрации, попробуй через 5 секунд")
        print(e)


# =========================
# Правила (текст + кнопка)
# =========================
RULES_TEXT = (
    "🛠️ <b>Бауманское братство — черновые правила</b>\n\n"
    "1) <b>Мы — одна команда.</b> Не мешаем другим, не спамим, не токсичим.\n"
    "2) <b>Инженерная честь.</b> Не используем баги/дыры для нечестной игры.\n"
    "3) <b>Дисциплина.</b> Админские решения по игре — финальные.\n"
    "4) <b>Братство.</b> Помогаем новичкам и не бросаем своих.\n"
    "5) <b>Чекпоинты.</b> Отмечаемся честно, без повторных отметок.\n"
    "6) <b>Заражение.</b> Тратим очки осознанно; игра заканчивается при 0 жизней.\n\n"
    "⚙️ <i>Это заглушка. Ты потом заменишь на нормальный текст.</i>"
)

@bot.message_handler(func=lambda message: message.text == "Правила")
def send_rules(message):
    bot.send_message(message.chat.id, RULES_TEXT, parse_mode="HTML")
    buttons(message)


# =========================
# Админ: /broadcast (рассылка)
# =========================
@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return

    # Просим текст для рассылки и переходим на следующий шаг
    msg = bot.send_message(message.chat.id, "✉️ Введи сообщение для рассылки:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users()
    text = message.text

    sent = 0
    failed = 0

    # Пытаемся отправить всем
    for user_id in users:
        try:
            bot.send_message(user_id, text)
            sent += 1
        except:
            failed += 1

    bot.send_message(message.chat.id, f"✅ Рассылка завершена\n"
                                      f"Отправлено: {sent}\n"
                                      f"Не доставлено: {failed}")


# =========================
# Админ: /addpoints (добавление очков команде)
# =========================
@bot.message_handler(commands=['addpoints'])
def adding(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return

    # Выбор команды кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))

    msg = bot.send_message(message.chat.id, "Выбери команду:", reply_markup=markup)
    bot.register_next_step_handler(msg, select_team_for_points)

def select_team_for_points(message):
    # Проверяем, что нажали кнопку команды
    if message.text not in teams:
        return

    # Запоминаем выбранную команду в admin_data
    admin_data[message.from_user.id] = message.text

    # Просим ввести число
    msg = bot.send_message(message.chat.id, "Введи количество очков:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, enter_points_amount)

def enter_points_amount(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        return

    # Число ли введено
    if not message.text.isdigit():
        return

    points_to_add = int(message.text)
    team_name = admin_data.get(message.from_user.id)

    try:
        # Находим строку команды в sheet_2 и обновляем очки (col2)
        cell = sheet_2.find(team_name)
        row = cell.row

        current = sheet_2.cell(row, 2).value
        current_points = int(current) if current else 0

        new_points = current_points + points_to_add
        sheet_2.update_cell(row, 2, new_points)

        bot.send_message(
            message.chat.id,
            f"Команда <b>{team_name}</b> получила <b>{points_to_add}</b> очков!\n"
            f"Теперь у неё: <b>{new_points}</b> очков",
            parse_mode="HTML"
        )

    except Exception as e:
        print("ADD POINTS ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА")


# =========================
# Админ: /check (отметка команды на чекпоинте)
# =========================
@bot.message_handler(commands=["check"])
def check_start(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return

    msg = bot.send_message(message.chat.id, "Введи номер чекпоинта (число):")
    bot.register_next_step_handler(msg, check_enter_checkpoint)

def check_enter_checkpoint(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        return

    # Проверяем число
    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "Введи номер чекпоинта ЦИФРОЙ:")
        bot.register_next_step_handler(msg, check_enter_checkpoint)
        return

    checkpoint = int(message.text)

    # Запоминаем чекпоинт
    admin_data[message.from_user.id] = {"checkpoint": checkpoint}

    # Дальше выбираем команду кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))

    msg = bot.send_message(message.chat.id, "Выбери команду:", reply_markup=markup)
    bot.register_next_step_handler(msg, check_choose_team)

def check_choose_team(message):
    # Только админ
    if message.from_user.id != ADMIN_ID:
        return

    if message.text not in teams:
        bot.send_message(message.chat.id, "Выбери команду.")
        return

    team_name = message.text
    checkpoint = admin_data.get(message.from_user.id, {}).get("checkpoint")

    if checkpoint is None:
        bot.send_message(message.chat.id, "Чекпоинт не задан")
        return

    try:
        # В sheet_3:
        # col1 — список чекпоинтов
        checkpoint_ids = sheet_3.col_values(1)
        checkpoint_str = str(checkpoint)

        if checkpoint_str not in checkpoint_ids:
            bot.send_message(message.chat.id, "чекпоинта нет в таблице.", reply_markup=types.ReplyKeyboardRemove())
            return

        # Строка нужного чекпоинта
        row = checkpoint_ids.index(checkpoint_str) + 1

        # Заголовки: первая строка — команды
        headers = sheet_3.row_values(1)
        if team_name not in headers:
            bot.send_message(message.chat.id, "не найдена в заголовках таблицы.", reply_markup=types.ReplyKeyboardRemove())
            return

        # Колонка нужной команды
        col = headers.index(team_name) + 1

        # Не отмечали ли уже?
        current = sheet_3.cell(row, col).value
        if current == "1":
            bot.send_message(message.chat.id, "команда уже отмечена на этом чекпоинте.", reply_markup=types.ReplyKeyboardRemove())
            return

        # Ставим отметку
        sheet_3.update_cell(row, col, 1)

        bot.send_message(
            message.chat.id,
            f"Отметил: <b>{team_name}</b> на чекпоинте <b>{checkpoint}</b>",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )

    except Exception as e:
        print("CHECKPOINT ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА", reply_markup=types.ReplyKeyboardRemove())


# =========================
# Статистика команд (очки + жизни)
# =========================
@bot.message_handler(func=lambda message: message.text == "Статистика")
def show_teams(message):
    try:
        points_and_teams = []

        # Берём строки 2..9 (8 команд) из sheet_2
        for i in range(2, 10):
            row = sheet_2.row_values(i)
            if len(row) >= 2:
                team_name = row[0]
                points = int(row[1]) if row[1] else 0
                life = int(row[2]) if row[2] else 0
                points_and_teams.append([team_name, points, life])

        # Сортируем по очкам (убывание)
        points_and_teams.sort(key=lambda x: -x[1])

        medals = ["🥇", "🥈", "🥉"]
        text = "🏆 <b>Таблица лидеров</b>\n\n"

        # Важно: тут распаковка трёх значений (team, points, life)
        for index, (team, points, life) in enumerate(points_and_teams):
            place = index + 1
            if index < 3:
                medal = medals[index]
                text += f"{medal} <b>{place} место</b> - {team} | {points} очков | {life} здоровья\n"
            else:
                text += f"{place} место - {team} | {points} очков | {life} здоровья\n"

        bot.send_message(message.chat.id, text, parse_mode="HTML")

    except Exception as e:
        print(e)
        bot.send_message(
            message.chat.id,
            "К огромному сожалению вы израсходовали количество запросов. пожалуйста повторите запрос через 30 секунд <3"
        )


# =========================
# Заражение (тратим очки → снимаем жизни другой команде)
# =========================
@bot.message_handler(func=lambda message: message.text == "Потратить очки заражения")
def infect_button(message):
    # Если команда мертва или юзер не зарегистрирован — стоп
    if deny_if_dead(message):
        return

    user_id = message.from_user.id
    team = get_user_team(user_id)

    if not team:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Нажми «Регистрация».")
        return

    # Запоминаем атакующую команду в сессии
    user_sessions[user_id] = {"attacker_team": team}

    # Показываем выбор цели (все команды кроме своей)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in teams:
        if t != team:
            markup.add(types.KeyboardButton(t))

    msg = bot.send_message(message.chat.id, "Выбери команду-цель:", reply_markup=markup)
    bot.register_next_step_handler(msg, infect_choose_target)


def infect_choose_target(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "Сессия сброшена. Начни заново.")
        return

    attacker_team = session["attacker_team"]
    target_team = message.text

    # Проверяем правильность выбора цели
    if target_team not in teams or target_team == attacker_team:
        bot.send_message(message.chat.id, "Выбери команду-цель кнопкой.")
        return

    session["target_team"] = target_team

    # Считываем очки/жизни атакующего
    attacker_points, attacker_life = read_points_and_life(attacker_team)

    # Просим сколько тратить
    msg = bot.send_message(
        message.chat.id,
        f"У вашей команды <b>{attacker_points}</b> очков заражения.\n"
        f"Сколько потратить, чтобы снять жизни у <b>{target_team}</b>?",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, infect_enter_amount)


# =========================
# Утилиты чтения/записи sheet_2 + связь user_id -> команда
# =========================
def get_user_team(user_id: int) -> str | None:
    # В sheet регистрации:
    # col1 = user_id, col4 = команда
    ids = sheet.col_values(1)
    teams_col = sheet.col_values(4)
    uid = str(user_id)

    for i in range(1, len(ids)):  # пропускаем заголовок
        if ids[i] == uid:
            return teams_col[i] if i < len(teams_col) else None
    return None


def get_team_row_in_sheet2(team_name: str) -> int:
    # Находим строку команды в sheet_2 (ищем в колонке 1)
    cell = sheet_2.find(team_name, in_column=1)
    return cell.row


def get_team_life(team_name: str) -> int:
    # Жизни команды = колонка 3
    cell = sheet_2.find(team_name, in_column=1)
    row = cell.row
    life = sheet_2.cell(row, 3).value
    return int(life) if life and str(life).isdigit() else 0


def read_points_and_life(team_name: str) -> tuple[int, int]:
    # Очки = col2, Жизни = col3
    row = get_team_row_in_sheet2(team_name)
    pts = sheet_2.cell(row, 2).value
    life = sheet_2.cell(row, 3).value
    pts_i = int(pts) if pts and str(pts).isdigit() else 0
    life_i = int(life) if life and str(life).isdigit() else 0
    return pts_i, life_i


def write_points_and_life(team_name: str, points: int, life: int):
    # Запись очков/жизней обратно в таблицу
    row = get_team_row_in_sheet2(team_name)
    sheet_2.update_cell(row, 2, points)
    sheet_2.update_cell(row, 3, life)


def infect_enter_amount(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "Сессия сброшена. Начни заново")
        return

    # Проверка на число
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введи число")
        return

    amount = int(message.text)

    if amount <= 0:
        bot.send_message(message.chat.id, "Нужно положительное число")
        return

    attacker_team = session["attacker_team"]
    target_team = session["target_team"]

    try:
        # Считываем текущее состояние
        attacker_points, attacker_life = read_points_and_life(attacker_team)
        target_points, target_life = read_points_and_life(target_team)

        # Проверка: хватает ли очков у атакующего
        if attacker_points < amount:
            bot.send_message(message.chat.id, f"Недостаточно очков. У вас: <b>{attacker_points}</b>", parse_mode="HTML")
            return

        # Если у цели уже 0 жизней
        if target_life <= 0:
            bot.send_message(message.chat.id, "У цели уже 0 жизней.")
            return

        # Обновляем очки/жизни
        new_attacker_points = attacker_points - amount
        new_target_life = max(0, target_life - amount)

        write_points_and_life(attacker_team, new_attacker_points, attacker_life)
        write_points_and_life(target_team, target_points, new_target_life)

        # Отчёт пользователю
        bot.send_message(
            message.chat.id,
            f"<b>{attacker_team}</b> потратила <b>{amount}</b> очков заражения на <b>{target_team}</b>\n"
            f"Очки вашей команды теперь: <b>{new_attacker_points}</b>\n"
            f"Жизни команды {target_team} теперь: <b>{new_target_life}</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        print("INFECT ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА при атаке.")

    finally:
        # В конце возвращаем меню и чистим сессию
        buttons(message)
        user_sessions.pop(user_id, None)


# =========================
# Проверка "мертва ли команда"
# =========================
def deny_if_dead(message) -> bool:
    # Получаем команду пользователя
    team = get_user_team(message.from_user.id)

    if not team:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return True

    # Смотрим жизни команды
    life = get_team_life(team)

    if life <= 0:
        bot.send_message(
            message.chat.id,
            "💀 <b>Твоя команда мертва.</b>\n Игра для вас окончена.\n",
            parse_mode="HTML"
        )
        return True

    return False


# =========================
# Запуск polling
# =========================
bot.polling(none_stop=True)
