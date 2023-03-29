import sqlite3
import telebot
from datetime import datetime
from telebot import types, util



conn = sqlite3.connect("database.db")
c = conn.cursor()

# Create a table for teachers
c.execute('''CREATE TABLE IF NOT EXISTS teacher
             (id INTEGER PRIMARY KEY, name TEXT, subject TEXT, telegram_id INTEGER)''')

# Create a table for complaints
c.execute('''CREATE TABLE IF NOT EXISTS complaint
             (id INTEGER PRIMARY KEY, user TEXT, teacher TEXT, reason TEXT, time TEXT)''')


BOT_TOKEN = '6029344631:AAGmv1EuUlplVAu0VH-3r2E_28LXuoNTDCw'

# Initialize the bot and provide the API key
bot = telebot.TeleBot(BOT_TOKEN)

# Define a function to handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Complaint Bot! Use /complain to lodge your complaint.")


def get_teachers():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Add the button

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM teacher")
    rows = c.fetchall()
    for row in rows:
        button = types.KeyboardButton(row[1])
        markup.add(button)

    return markup


@bot.message_handler(commands=['complaint'])
def complaint_main(message):
    bot.reply_to(message, 'Assalomu aleykum! Shikoyat yuborish uchun birinchi navbatda ismingizni kiriting: ')
    bot.register_next_step_handler(message, get_user_name)



def get_user_name(message):
    user_name = message.text


    bot.reply_to(message, "Qaysi o'qituvchiga shikoyat yuborasiz?", reply_markup=get_teachers())
    bot.register_next_step_handler(message, get_teacher_name, user_name)


def get_teacher_name(message, user_name):

    teacher_name = message.text

    bot.reply_to(message, 'Shikoyatingiz haqida batafsil yozing: ', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_complaint, user_name, teacher_name)


def save_complaint(message, user_name, teacher_name):
    reason = message.text
    # Connect to the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    time = datetime.now()
    c.execute("INSERT INTO complaint (user, teacher, reason, time) VALUES (?, ?, ?, ?)", (user_name, teacher_name, reason, time))
    conn.commit()

    conn.close()

    bot.reply_to(message, "Shikoyatingiz qabul qilindi!")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM teacher WHERE name=?", (teacher_name,))
    teacher = c.fetchone()
    bot.send_message(teacher[-1], f'Sizga yangi shikoyat tushdi. Sabab:{reason}')



@bot.message_handler(commands=['admin'])
def start_command(message):
    # Create an inline keyboard with two buttons
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="O'qituvchi qo'shish", callback_data="add_teacher")
    button2 = types.InlineKeyboardButton(text="O'qituvchi o'chirish", callback_data="delete_teacher")
    keyboard.add(button1, button2)

    # Send a message with the inline keyboard
    bot.send_message(chat_id=message.chat.id, text="Choose an option:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "add_teacher":
        bot.answer_callback_query(callback_query_id=call.id, text="O'qituvchi qo'shishni bosdingiz!")
        bot.send_message(call.message.chat.id, "Qo'shmoqchi bo'lgan o'qituvchining to'liq ismini kiriting: ")
        bot.register_next_step_handler(call.message, get_teacher_name2)

    elif call.data == 'delete_teacher':
        bot.answer_callback_query(callback_query_id=call.id, text="O'qituvchi o'chirishni bosdingiz!")
        bot.send_message(call.message.chat.id, "O'chirmoqchi bo'lgan o'qituvchingizni tanlang", reply_markup=get_teachers())
        bot.register_next_step_handler(call.message, delete_teacher)


def delete_teacher(message):
    teacher_name = message.text
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM teacher WHERE name=?", (teacher_name,))
    conn.commit()

    bot.send_message(message.chat.id, f"Siz {teacher_name}ni muvaffaqiyatli o'chirdingiz", reply_markup=telebot.types.ReplyKeyboardRemove())



def get_teacher_name2(message):
    teacher_name = message.text
    bot.reply_to(message, 'Fan nomini kiriting: ')
    bot.register_next_step_handler(message, get_subject, teacher_name)

def get_subject(message, teacher_name):
    subject = message.text
    bot.reply_to(message, "O'qituvchining telegram id sini kiriting: ")
    bot.register_next_step_handler(message, save_teacher, teacher_name, subject)


def save_teacher(message, teacher_name, subject):
    telegram_id = message.text
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO teacher (name, subject, telegram_id) VALUES (?, ?, ?)", (teacher_name, subject, telegram_id))
    conn.commit()
    conn.close()
    bot.reply_to(message, "Muvaffaqiyatli qo'shdingiz!")
    bot.send_message(telegram_id, f"{teacher_name}, siz o'qituvchilar ro'yhatiga muvaffaqiyatli qo'shildingiz!")



# Run the bot
bot.polling()
