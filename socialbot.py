import telebot
import sqlite3

bot = telebot.TeleBot('7095896339:AAFGoS-2cO_4fG2M-Yf7RUdsRJS_6m3KI4E')

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
    
    else:
        bot.send_message(chat_id, "Напиши /start, чтобы начать процесс регистрации.")

bot.infinity_polling()

conn.close()
