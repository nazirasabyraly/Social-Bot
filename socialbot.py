import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
bot = telebot.TeleBot('7095896339:AAFGoS-2cO_4fG2M-Yf7RUdsRJS_6m3KI4E')

button_anim = KeyboardButton('Помощь животным')
button_eco = KeyboardButton('Эко мероприятия')
button_vet = KeyboardButton('Помощь ветеринарам')

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb.add(button_anim, button_eco, button_vet)

# Подключение к базе данных socialbot
conn = sqlite3.connect('socialbot.db', uri=True, check_same_thread=False)
cursor = conn.cursor()

# Словарь для отслеживания состояния пользователей
user_states = {}

# Хендлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Проверяем, зарегистрирован ли пользователь
    cursor.execute("SELECT * FROM userss WHERE id = ?", (chat_id,))
    result = cursor.fetchone()
    
    if result is None:
        bot.send_message(chat_id, "Привет! Напиши свое имя и фамилию, чтобы зарегистрироваться.")
        user_states[chat_id] = 'awaiting_name_surname'
    else:
        bot.send_message(chat_id, f"Ты уже зарегистрирован как {result[1]}, секция: {result[2]}.")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    score = 0
    # Если мы ждем имя и фамилию
    if chat_id in user_states and user_states[chat_id] == 'awaiting_name_surname':
        full_name = text
        bot.send_message(chat_id, "Теперь выбери секцию социальной работы, в которую хочешь пойти.")
        user_states[chat_id] = {'full_name': full_name, 'state': 'awaiting_section_choice'}
    
    # Если мы ждем выбор секции
    elif chat_id in user_states and isinstance(user_states[chat_id], dict) and user_states[chat_id]['state'] == 'awaiting_section_choice':
        section = text
        full_name = user_states[chat_id]['full_name']
        
        # Вставляем нового пользователя в таблицу users
        cursor.execute("INSERT INTO userss (id, name, section, score) VALUES (?, ?, ?, ?)", 
                       (chat_id, full_name, section, score)) 
        conn.commit()
        
        bot.send_message(chat_id, f"Ты зарегистрирован! Имя: {full_name}, Секции: {section}.")
        user_states.pop(chat_id, None)

# Хендлер для команды /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    chat_id = message.chat.id
    
    # Debugging message to confirm the command is received
    print("/menu command received")
    bot.send_message(chat_id, "Вызываю меню...")

    # Send message with keyboard
    bot.send_message(message.chat.id, "Выбери мероприятие:", reply_markup=greet_kb)
  

bot.infinity_polling()

conn.close()

# import telebot
# import sqlite3
# from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# bot_token = '7095896339:AAFGoS-2cO_4fG2M-Yf7RUdsRJS_6m3KI4E'
# bot = telebot.TeleBot(bot_token)

# # Define keyboard buttons
# button_anim = KeyboardButton('Помощь животным')
# button_eco = KeyboardButton('Эко мероприятия')
# button_vet = KeyboardButton('Помощь ветеринарам')

# # Create the reply keyboard
# greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
# greet_kb.add(button_anim, button_eco, button_vet)

# # Connect to the SQLite database
# conn = sqlite3.connect('socialbot.db', check_same_thread=False)
# cursor = conn.cursor()

# # Dictionary to track user states
# user_states = {}

# # Handler for /start command
# @bot.message_handler(commands=['start'])
# def start(message):
#     chat_id = message.chat.id
#     try:
#         cursor.execute("SELECT * FROM userss WHERE id = ?", (chat_id,))
#         result = cursor.fetchone()
#         if result is None:
#             bot.send_message(chat_id, "Привет! Напиши свое имя и фамилию, чтобы зарегистрироваться.")
#             user_states[chat_id] = 'awaiting_name_surname'
#         else:
#             bot.send_message(chat_id, f"Ты уже зарегистрирован как {result[1]}, секция: {result[2]}.")
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#         bot.send_message(chat_id, "Ошибка доступа к базе данных.")

# # Handler for text messages
# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     chat_id = message.chat.id
#     text = message.text.strip()
#     if chat_id in user_states:
#         try:
#             if user_states[chat_id] == 'awaiting_name_surname':
#                 full_name = text
#                 bot.send_message(chat_id, "Теперь выбери секцию социальной работы, в которую хочешь пойти.")
#                 user_states[chat_id] = {'full_name': full_name, 'state': 'awaiting_section_choice'}
#             elif 'state' in user_states[chat_id] and user_states[chat_id]['state'] == 'awaiting_section_choice':
#                 section = text
#                 full_name = user_states[chat_id]['full_name']
#                 cursor.execute("INSERT INTO userss (id, name, section, score) VALUES (?, ?, ?, 0)",
#                                (chat_id, full_name, section))
#                 conn.commit()
#                 bot.send_message(chat_id, f"Ты зарегистрирован! Имя: {full_name}, Секции: {section}.")
#                 user_states.pop(chat_id, None)
#         except sqlite3.Error as e:
#             print(f"Database error: {e}")
#             bot.send_message(chat_id, "Ошибка при работе с базой данных.")

# # Handler for /menu command
# @bot.message_handler(commands=['menu'])
# def menu(message):
#     chat_id = message.chat.id
#     print("/menu command received")
#     bot.send_message(chat_id, "Выбери мероприятие:", reply_markup=greet_kb)
#     print("Menu sent with options")

# if __name__ == '__main__':
#     try:
#         bot.polling(none_stop=True)
#     except Exception as e:
#         print(f"Polling error: {e}")

# conn.close()
