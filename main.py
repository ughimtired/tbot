# Телеграм-бот v.004
from io import BytesIO

import telebot  # pyTelegramBotAPI 4.3.1
from telebot import types
import requests
import bs4
import botGames  # бот-игры, файл botGames.py
import menuBot
from menuBot import Menu, Users  # в этом модуле есть код, создающий экземпляры классов описывающих моё меню
import DZ  # домашнее задание от первого урока
import SECRET  # секретные ключи, пароли
import time

bot = telebot.TeleBot(SECRET.TELEGRAM_TOKEN)  # Создаем экземпляр бота


# -----------------------------------------------------------------------
# Функция, обрабатывающая команды
@bot.message_handler(commands="start")
def command(message, res=False):
    chat_id = message.chat.id
    bot.send_sticker(chat_id, "CAACAgIAAxkBAAIaeWJEeEmCvnsIzz36cM0oHU96QOn7AAJUAANBtVYMarf4xwiNAfojBA")
    txt_message = f"Привет, {message.from_user.first_name}! Я тестовый бот для курса программирования на языке Python"
    bot.send_message(chat_id, text=txt_message, reply_markup=Menu.getMenu(chat_id, "Главное меню").markup)


# -----------------------------------------------------------------------
# Получение стикеров от юзера
@bot.message_handler(content_types=['sticker'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    sticker = message.sticker
    bot.send_message(message.chat.id, sticker)

    # глубокая инспекция объекта
    # import inspect,pprint
    # i = inspect.getmembers(sticker)
    # pprint.pprint(i)


# -----------------------------------------------------------------------
# Получение аудио от юзера
@bot.message_handler(content_types=['audio'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    audio = message.audio
    bot.send_message(chat_id, audio)


# -----------------------------------------------------------------------
# Получение голосовухи от юзера
@bot.message_handler(content_types=['voice'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    voice = message.voice
    bot.send_message(message.chat.id, voice)


# -----------------------------------------------------------------------
# Получение фото от юзера
@bot.message_handler(content_types=['photo'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    photo = message.photo
    bot.send_message(message.chat.id, photo)


# -----------------------------------------------------------------------
# Получение видео от юзера
@bot.message_handler(content_types=['video'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    video = message.video
    bot.send_message(message.chat.id, video)


# -----------------------------------------------------------------------
# Получение документов от юзера
@bot.message_handler(content_types=['document'])
def get_messages(message):
    chat_id = message.chat.id
    mime_type = message.document.mime_type
    bot.send_message(chat_id, "Это " + message.content_type + " (" + mime_type + ")")

    document = message.document
    bot.send_message(message.chat.id, document)
    if message.document.mime_type == "video/mp4":
        bot.send_message(message.chat.id, "This is a GIF!")


# -----------------------------------------------------------------------
# Получение координат от юзера
@bot.message_handler(content_types=['location'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    location = message.location
    bot.send_message(message.chat.id, location)

    from Weather import WeatherFromPyOWN
    pyOWN = WeatherFromPyOWN()
    bot.send_message(chat_id, pyOWN.getWeatherAtCoords(location.latitude, location.longitude))
    bot.send_message(chat_id, pyOWN.getWeatherForecastAtCoords(location.latitude, location.longitude))


# -----------------------------------------------------------------------
# Получение контактов от юзера
@bot.message_handler(content_types=['contact'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    contact = message.contact
    bot.send_message(message.chat.id, contact)


# -----------------------------------------------------------------------
# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    ms_text = message.text

    cur_user = Users.getUser(chat_id)
    if cur_user == None:
        cur_user = Users(chat_id, message.json["from"])

    # проверка = мы нажали кнопку подменю, или кнопку действия
    subMenu = menuBot.goto_menu(bot, chat_id, ms_text)  # попытаемся использовать текст как команду меню, и войти в него
    if subMenu != None:
        # Проверим, нет ли обработчика для самого меню. Если есть - выполним нужные команды
        if subMenu.name == "Игра в 21":
            game21 = botGames.newGame(chat_id, botGames.Game21(jokers_enabled=True))  # создаём новый экземпляр игры
            text_game = game21.get_cards(2)  # просим 2 карты в начале игры
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

        elif subMenu.name == "Игра больше-меньше":
            bot.send_message(chat_id, text='Правила игры "больше-меньше":\n'
                                           'перед вами карта из колоды состоящая из 52 карт. Вам нужно отгадать, будет ли следующая карты номиналом больше или меньше')
            gameML = botGames.newGame(chat_id, botGames.GameMoreLess())
            text_game = gameML.get_cards(1)
            bot.send_media_group(chat_id, media=getMediaCards(gameML))  # получим и отпим изображения карт
            bot.send_message(chat_id, text=text_game)

        elif subMenu.name == "Камень, ножницы, бумага":
            gameRSP = botGames.newGame(chat_id, botGames.GameRPS())  # создаём новый экземпляр игры и регистрируем его
            text_game = "<b>Победитель определяется по следующим правилам:</b>\n" \
                        "1. Камень побеждает ножницы\n" \
                        "2. Бумага побеждает камень\n" \
                        "3. Ножницы побеждают бумагу\n" \
                        "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
            bot.send_photo(chat_id, photo="https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg", caption=text_game,
                           parse_mode='HTML')

        return  # мы вошли в подменю, и дальнейшая обработка не требуется

    # проверим, является ли текст текущий команды кнопкой действия
    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu != None and ms_text in cur_menu.buttons:  # проверим, что команда относится к текущему меню

        if ms_text == "Помощь":
            send_help(chat_id)

        # ======================================= Развлечения
        elif ms_text == "Прислать собаку":
            bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собачка!")

        elif ms_text == "Прислать лису":
            bot.send_photo(chat_id, photo=get_foxURL(), caption="Вот тебе лисичка!")

        elif ms_text == "Прислать анекдот":
            bot.send_message(chat_id, text=get_anekdot())

        elif ms_text == "Прислать подкат":
            bot.send_message(chat_id, text=get_pickup())

        elif ms_text == "Прислать фильм":
            send_film(chat_id)

        elif ms_text == "Угадай кто?":
            get_ManOrNot(chat_id)

        # ======================================= реализация игры в 21
        elif ms_text == "Карту!":
            game21 = botGames.getGame(chat_id)
            if game21 == None:  # если мы случайно попали в это меню, а объекта с игрой нет
                menuBot.goto_menu(bot, chat_id, "Выход")
                return

            text_game = game21.get_cards(1)
            bot.send_media_group(chat_id, media=getMediaCards(game21))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

            if game21.status != None:  # выход, если игра закончена
                botGames.stopGame(chat_id)
                menuBot.goto_menu(bot, chat_id, "Выход")
                return

        elif ms_text == "Стоп!":
            botGames.stopGame(chat_id)
            menuBot.goto_menu(bot, chat_id, "Выход")
            return

        # =======================================больше меньше

        elif ms_text in botGames.GameMoreLess.values:
            gameML = botGames.getGame(chat_id)
            if gameML == None:
                menuBot.goto_menu(bot, chat_id, "Выход")
                return

            text_game = gameML.get_cards(1, ms_text)
            bot.send_media_group(chat_id, media=getMediaCards(gameML))  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)
            if gameML.status != None:  # выход, если игра закончена
                botGames.stopGame(chat_id)
                menuBot.goto_menu(bot, chat_id, "Выход")
                return

        # ======================================= реализация игры Камень-ножницы-бумага
        elif ms_text in botGames.GameRPS.values:
            gameRSP = botGames.getGame(chat_id)
            if gameRSP == None:  # если мы случайно попали в это меню, а объекта с игрой нет
                menuBot.goto_menu(bot, chat_id, "Выход")
                return
            text_game = gameRSP.playerChoice(ms_text)
            bot.send_message(chat_id, text=text_game)
            gameRSP.newGame()

        # ======================================= реализация игры Камень-ножницы-бумага Multiplayer
        elif ms_text == "КНБ Multiplayer":
            keyboard = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(text="Создать новую игру", callback_data="GameRPSm|newGame")
            keyboard.add(btn)
            numGame = 0
            for game in botGames.activeGames.values():
                if type(game) == botGames.GameRPS_Multiplayer:
                    numGame += 1
                    btn = types.InlineKeyboardButton(text="Игра КНБ-" + str(numGame) + " игроков: " + str(len(game.players)), callback_data="GameRPSm|Join|" + menuBot.Menu.setExtPar(game))
                    keyboard.add(btn)
            btn = types.InlineKeyboardButton(text="Вернуться", callback_data="GameRPSm|Exit")
            keyboard.add(btn)

            bot.send_message(chat_id, text=botGames.GameRPS_Multiplayer.name, reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id, "Вы хотите начать новую игру, или присоединиться к существующей?", reply_markup=keyboard)


        # ======================================= модуль ДЗ
        elif ms_text == "Задание-1":
            DZ.dz1(bot, chat_id)

        elif ms_text == "Задание-2":
            DZ.dz2(bot, chat_id)

        elif ms_text == "Задание-3":
            DZ.dz3(bot, chat_id)

        elif ms_text == "Задание-4":
            DZ.dz4(bot, chat_id)

        elif ms_text == "Задание-5":
            DZ.dz5(bot, chat_id)

        elif ms_text == "Задание-6":
            DZ.dz6(bot, chat_id)
        # ======================================= случайный текст
    else:
        bot.send_message(chat_id, text="Мне жаль, я не понимаю вашу команду: " + ms_text)
        menuBot.goto_menu(bot, chat_id, "Главное меню")


# -----------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # если требуется передать параметр или несколько параметров в обработчик кнопки,
    # используйте методы Menu.getExtPar() и Menu.setExtPar()
    # call.data это callback_data, которую мы указали при объявлении InLine-кнопки
    # После обработки каждого запроса вызовете метод answer_callback_query(), чтобы Telegram понял, что запрос обработан
    chat_id = call.message.chat.id
    message_id = call.message.id
    cur_user = Users.getUser(chat_id)
    if cur_user == None:
        cur_user = Users(chat_id, call.message.json["from"])

    tmp = call.data.split("|")
    menu = tmp[0] if len(tmp) > 0 else ""
    cmd = tmp[1] if len(tmp) > 1 else ""
    par = tmp[2] if len(tmp) > 2 else ""



    if menu == "GameRPSm":

        if cmd == "newGame":
            # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
            bot.delete_message(chat_id, message_id)
            botGames.newGame(chat_id, botGames.GameRPS_Multiplayer(bot, cur_user))
            bot.answer_callback_query(call.id)

        elif cmd == "Join":
            # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
            bot.delete_message(chat_id, message_id)
            gameRSPMult = Menu.getExtPar(par)
            if gameRSPMult is None:  # если наткнулись на кнопку, которой быть не должно
                return
            else:
                gameRSPMult.addPlayer(cur_user.id, cur_user.userName)
            bot.answer_callback_query(call.id)

        elif cmd == "Exit":
            bot.delete_message(chat_id, message_id)
            gameRSPMult = Menu.getExtPar(par)
            if gameRSPMult is not None:
                gameRSPMult.delPlayer(cur_user.id)
            menuBot.goto_menu(bot, chat_id, "Игры")
            bot.answer_callback_query(call.id)

        elif "Choice-" in cmd:
            gameRSPMult = Menu.getExtPar(par)
            if gameRSPMult is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
                bot.delete_message(chat_id, message_id)
            else:
                choice = cmd[7:]
                gameRSPMult.playerChoice(cur_user.id, choice)
            bot.answer_callback_query(call.id)


# -----------------------------------------------------------------------
def getMediaCards(game21):
    medias = []
    for url in game21.arr_cards_URL:
        medias.append(types.InputMediaPhoto(url))
    return medias


# -----------------------------------------------------------------------
def send_help(chat_id):
    global bot
    bot.send_message(chat_id, "Автор: Пиличева Мария")
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Напишите автору", url="https://t.me/mariachichy")
    markup.add(btn1)
    img = open('M.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=markup)

    bot.send_message(chat_id, "Активные пользователи чат-бота:")
    for el in Users.activeUsers:
        bot.send_message(chat_id, Users.activeUsers[el].getUserHTML(), parse_mode='HTML')


# -----------------------------------------------------------------------
def send_film(chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n" \
               f"Год: {film['Год']}\n" \
               f"Страна: {film['Страна']}\n" \
               f"Жанр: {film['Жанр']}\n" \
               f"Продолжительность: {film['Продолжительность']}"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="СМОТРЕТЬ онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML', reply_markup=markup)


# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
def get_anekdot():
    array_anekdots = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdots.append(result.getText().strip())
    if len(array_anekdots) > 0:
        return array_anekdots[0]
    else:
        return ""

def get_pickup():
    array_flirt = []
    reg_flirt = requests.get('https://www.generatormix.com/random-pick-up-lines')
    if reg_flirt.status_code == 200 :
        soup = bs4.BeautifulSoup(reg_flirt.text, "html.parser")
        result_find = soup.select('.col-12.tile-block-inner.marg-top.first')
        for result in result_find:
            array_flirt.append(result.getText().strip())
    if len(array_flirt) > 0:
        return array_flirt[0]
    else:
        return ""

# -----------------------------------------------------------------------

def get_foxURL():
    url = ""
    req = requests.get('https://randomfox.ca/floof/')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['image']
        # url.split("/")[-1]
    return url

# -----------------------------------------------------------------------
def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
        # url.split("/")[-1]
    return url


# -----------------------------------------------------------------------
def get_ManOrNot(chat_id):
    global bot

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Проверить",
                                      url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")
    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")


# ---------------------------------------------------------------------
def get_randomFilm():
    url = 'https://randomfilm.ru/'
    infoFilm = {}
    req_film = requests.get(url)
    soup = bs4.BeautifulSoup(req_film.text, "html.parser")
    result_find = soup.find('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]

    details = result_find.findAll('td')
    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm


# ---------------------------------------------------------------------


bot.polling(none_stop=True, interval=0)  # Запускаем бота

print()