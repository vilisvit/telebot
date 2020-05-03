import telebot
import requests
import pyowm
import time
import apiai, json
from random import randint

print(telebot.__file__)

site=''
username=''
password=''
contest_id=''
problem_id=''
source_code=''
lang_id=''
session = requests.Session()

OWM_API = open("owm-api.txt", "r").read()
BOT_TOKEN = open("telegram-bot-token.txt", "r").read()
DIALOG_FLOW_TOKEN = open("dialog-flow-token.txt", "r").read()

bot = telebot.TeleBot(BOT_TOKEN)
owm = pyowm.OWM(OWM_API)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    from telebot import types
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/help')
    itembtn2 = types.KeyboardButton('/weather')
    itembtn3 = types.KeyboardButton('/joke')
    keyboard.add(itembtn1, itembtn2, itembtn3)
    bot.reply_to(message, "Привет, я телегамм бот Виталик!", reply_markup=keyboard)

@bot.message_handler(commands=["help"])
def send_help(message):
    s='''Вот мои команды:
/help - помощь
/weather - погода на текущий момент
/joke - рандомная шутка из интернета
/dots - загрузка решений в тестирующую систему DOTS для задач по программированию
Также я реагирую на различные типы сообщений.
Можешь просто пообщаться со мной!'''
    bot.send_message(message.chat.id, s)

@bot.message_handler(commands=["weather"])
def ask_city (message):
    sent = bot.send_message(message.chat.id, """Введи название своего населенного пункта.

Внимание: если существует нестколько населенных пунктов с таким названием, выведется погода по одному из них.""")
    bot.register_next_step_handler(sent, send_weather)
def send_weather (message):
    try:
        observation = owm.weather_at_place(message.text)
        w = observation.get_weather()
        t = w.get_temperature('celsius')['temp']
        wi = w.get_wind()['speed']
        h = w.get_humidity()
        bot.send_message(message.chat.id, f"На улице {t} градусов, влажность {h}% Скорость ветра: {wi} м/с.")
        if t<-20:
            bot.send_message(message.chat.id, "Ты куда это задумал идти в такой мороз?")
        elif -20<=t<0:
            bot.send_message(message.chat.id, "Одевай зимнюю куртку!")
        elif 0<=t<10:
            bot.send_message(message.chat.id, "Без шапки не пущу!")
        elif 10<=t<20:
            bot.send_message(message.chat.id, "Оденься полегче")
        elif 20<=t<30:
            bot.send_message(message.chat.id, "Можно выходить хоть в майке и трусах.")
        else:
            bot.send_message(message.chat.id, "Не знаю где жарче в печке или на улице...")
    except:
        bot.send_message(message.chat.id, f"Я не могу найти населенный пункт с названием {message.text}")

@bot.message_handler(commands=["dots"])
def ask_site (message):
    sent = bot.send_message(message.chat.id, """Команда /exit для выхода. 
Введи название сайта тестирующей системы DOTS (q-bit)""")
    bot.register_next_step_handler(sent, ask_username)
def ask_username (message):
    if message.text=="/exit":
        return
    global site
    site=message.text
    try:
        r = requests.get(f"https://{site}.dots.org.ua")
        r.encoding = "utf-8"
        page_text = r.text
        bot.send_message(message.chat.id, page_text[page_text.find("<title>") + len("<title>") : page_text.find("</title>")])
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так")
        return
    sent = bot.send_message(message.chat.id, "Введи логин от системы")
    bot.register_next_step_handler(sent, ask_password)
def ask_password (message):
    if message.text=="/exit":
        return
    global username
    username=message.text
    sent = bot.send_message(message.chat.id, "Введи пароль от системы. Обещаю, что никому его не расскажу")
    bot.register_next_step_handler(sent, ask_contest_id)
def ask_contest_id (message):
    if message.text=="/exit":
        return
    global username
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id-1)
    password=message.text
    login_form = {
        "from": "",
        "username": username,
        "password": password,
    }
    r = session.post(f"https://{site}.dots.org.ua/login", data=login_form)
    r = session.get(f"http://{site}.dots.org.ua/contests")
    r.encoding = "utf-8"
    contests_page = r.text
    contests_page = contests_page[contests_page.find('<a href="contests?id') :]
    res="Доступные турниры:\n"
    while contests_page.find('<a href="contests?id') != -1:
        if contests_page.find(">")+1 == contests_page.find('<font color="red">'):
            res+=contests_page[contests_page.find('<font color="red">')+18 : contests_page.find("</font>")]
            res+=" ID="+contests_page[contests_page.find('<a href="contests?id=')+21 : contests_page.find('">')]+"\n"
        else:
            res+=contests_page[contests_page.find(">")+1 : contests_page.find("</a>")]
            res+=" ID="+contests_page[contests_page.find('<a href="contests?id=')+21 : contests_page.find('">')]+"\n"
        contests_page = contests_page[contests_page.find('<a href="contests?id', 1) :]
    if res.strip()=="Доступные турниры:":
        bot.send_message(message.chat.id, "Нет доступных турниров")
        return
    else:
        print(res.strip())
        bot.send_message(message.chat.id, res)
    sent = bot.send_message(message.chat.id, "Введи ID контеста (турнира)")
    bot.register_next_step_handler(sent, ask_problem_id)
def ask_problem_id (message):
    if message.text=="/exit":
        return
    global contest_id
    global site
    contest_id=message.text
    try:
        r = session.get(f"http://{site}.dots.org.ua/contests?login={contest_id}")
        r.encoding = "utf-8"
        page_text = r.text
        bot.send_message(message.chat.id, page_text[page_text.find("<title>") + len("<title>") : page_text.find("</title>")])
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так")
        return
    r = session.get(f"http://{site}.dots.org.ua/problems")
    r.encoding = "utf-8"
    problems_page = r.text
    problems_page = problems_page[problems_page.find('<td class="pt" ><a href="problems?id=', 1) :]
    res="Доступные задачи:"
    while problems_page.find('<td class="pt" ><a href="problems?id=') != -1:
        res+=problems_page[problems_page.find('">')+2 : problems_page.find('</a>')]
        res+=" ID="+problems_page[problems_page.find('<td class="pt" ><a href="problems?id=')+36 : problems_page.find('">')]+"\n"
        problems_page = problems_page[problems_page.find('<td class="pt" ><a href="problems?id=', 1) :]
    if res.strip()=="Доступные задачи:\n":
        bot.send_message(message.chat.id, "Нет доступных задач")
        return
    else:
        bot.send_message(message.chat.id, res)
    sent = bot.send_message(message.chat.id, "Введи ID задачи")
    bot.register_next_step_handler(sent, ask_lang_id)
def ask_lang_id (message):
    if message.text=="/exit":
        return
    global problem_id
    problem_id=message.text
    sent = bot.send_message(message.chat.id, "Введи ID языка программирования")
    bot.register_next_step_handler(sent, ask_source_code)
def ask_source_code (message):
    if message.text=="/exit":
        return
    global lang_id
    lang_id=message.text
    sent = bot.send_message(message.chat.id, "Введи решение задачи")
    bot.register_next_step_handler(sent, send_source_code)
def send_source_code (message):
    if message.text=="/exit":
        return
    global source_code
    source_code=message.text
    solution_form = {
        "new": "2",
        "MAX_FILE_SIZE": "2097152",
        "pid": problem_id,
        "lang": lang_id,
        "ctype": "F",
        "source": source_code,
    }
    try:
        r = session.post(f"http://{site}.dots.org.ua/solutions", data=solution_form)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так")
        return
    if r.status_code==200:
        bot.send_message(message.chat.id, "Решение успешно отпралено")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так")

@bot.message_handler(commands=['joke'])
def send_joke(message):
    joke_res = requests.get('http://rzhunemogu.ru/RandJSON.aspx?CType=1')
    the_best_joke = str(joke_res.text)
    res = ''
    for i in range(12, len(the_best_joke) - 2):
        res += the_best_joke[i]
    bot.send_message(message.chat.id, res)

@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, "Вот мои команды: \n /help \n /start")

@bot.message_handler(content_types=["sticker"])
def echo_sticker(message):
    bot.reply_to(message, "Прикольный стикер!")

@bot.message_handler(content_types=["voice"])
def echo_sticker(message):
    voice = open('hello.mp3', 'rb')
    bot.send_voice(message.chat.id, voice)

@bot.message_handler(content_types=["location"])
def echo_sticker(message):
    bot.reply_to(message, "Где это?")

@bot.message_handler(content_types=["new_chat_title"])
def echo_sticker(message):
    bot.reply_to(message, "О, новое название чата!")

@bot.message_handler(content_types=["new_chat_members"])
def echo_sticker(message):
    bot.reply_to(message, "Приветствую в чате!")

@bot.message_handler(content_types=["photo"])
def echo_sticker(message):
    photo = open('koza.jfif', 'rb')
    bot.send_photo(message.chat.id, photo)

@bot.message_handler(content_types=["new_chat_photo"])
def echo_sticker(message):
    if randint(0, 2)==0:
        bot.reply_to(message, "Хорошая новая фотка у чата")
    else:
        bot.reply_to(message, "А мне больше старая нравилась")

@bot.message_handler()
def echo(message):
    print(message)
    if message.chat.id!=826325804:
        bot.forward_message(826325804, message.chat.id, message.message_id)
    split_message = message.text.lower().replace(",", "").replace(".", "").replace("?", "").replace(".!", "").split()
    if split_message[0]=="скажи":
        result=""
        for i in range(1, len(split_message)):
            result+=split_message[i]+" "
        bot.send_message(message.chat.id, result)
    elif "привет" in split_message:
        bot.reply_to(message, f"Привет, {message.from_user.first_name}")
    elif "здравствуй" in split_message:
        bot.reply_to(message, f"Здравствуй, {message.from_user.first_name}")
    elif "как дела" in split_message:
        bot.send_message(message.chat.id, "У меня все отлично")
    elif "как тебя зовут" in split_message:
        bot.send_message(message.chat.id, f"Я телеграм бот Виталик, приятно познакомиться, {message.from_user.first_name}")
    elif "пока" in split_message or "до свидания" in split_message:
        bot.send_message(message.chat.id, f"Пока, {message.from_user.first_name}")
    elif "погода" in split_message:
        bot.send_message(message.chat.id, "Воспользуйся командой /weather, чтобы узнать погоду")
    elif message.text.lower() == "помощь" or message.text.lower() == "помоги" or message.text.lower() == "помоги мне":
        bot.send_message(message.chat.id, "Воспользуйся командой /help, если нужна помощь")
    else:
        request = apiai.ApiAI(DIALOG_FLOW_TOKEN).text_request() # Токен API к Dialogflow
        request.lang = 'ru' # На каком языке будет послан запрос
        request.session_id = 'vit-bot-csukuj' # ID Сессии диалога (нужно, чтобы потом учить бота)
        request.query = message.text # Посылаем запрос к ИИ с сообщением от юзера
        responseJson = json.loads(request.getresponse().read().decode('utf-8'))
        response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
        # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
        if response:
            bot.reply_to(message, response)
        else:
            bot.reply_to(message, 'Я Вас не совсем понял!')
            
while True:
    try:
        bot.polling()
    except:
        print("Bot.polling() error")
        time.sleep(5)
