import telebot
import mcfg_abd
import abd_fun

bot = telebot.TeleBot(mcfg_abd.bot_token)

@bot.message_handler(commands=['start'])
def start_f(message):
    abd_fun.start(message)

@bot.message_handler(commands=['show'])
def start(message):
    abd_fun.show(message)

@bot.message_handler(commands=['showall'])
def start(message):
    abd_fun.show(message,all=True)

@bot.message_handler(commands=['turnoff'])
def start(message):
    abd_fun.turnoff(message)

@bot.message_handler(commands=['dash'])
def dash(message):
    abd_fun.dash(message)

@bot.message_handler()
def handle_text(message):
    delimetr = '\n'
    if abd_fun.check_admin(message):
        first_word = message.text.split(delimetr)[0].lower().strip()
        if first_word == 'добавить':
            abd_fun.add_deadline(message)
        elif first_word == 'убрать':
            abd_fun.remove_deadline(message)
        else:
            abd_fun.default_message(message)
    else:
        abd_fun.default_message(message)

bot.polling(none_stop=True, interval=1)
