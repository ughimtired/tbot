# -----------------------------------------------------------------------
def dz1(bot, chat_id):
    my_inputStr(bot, chat_id, "Как тебя зовут?", dz1_helper)


def dz1_helper(bot, chat_id, name_int):
    bot.send_message(chat_id, text="привет " + name_int.title())


# -----------------------------------------------------------------------
def dz2(bot, chat_id):
    my_inputInt(bot, chat_id, "сколько тебе лет?", dz2_helper)


def dz2_helper(bot, chat_id, age_int):
    if 18 > age_int > 10:
        bot.send_message(chat_id, 'какой ты малыш')
    elif 18 <= age_int <= 100:
        bot.send_message(chat_id, 'мое уважение, старпер')
    else:
        bot.send_message(chat_id, 'некорректные данные')


# -----------------------------------------------------------------------
def dz3(bot, chat_id):
    my_inputStr(bot, chat_id, "Как тебя зовут?", dz3_helper)


def dz3_helper(bot, chat_id, name_int):
    bot.send_message(chat_id, name_int * 5)


# -----------------------------------------------------------------------
def dz4(bot, chat_id):
    my_inputStr(bot, chat_id, "Как тебя зовут?", dz4_helper)


def dz4_helper(bot, chat_id, name_int):
    bot.send_message(chat_id, text="привет " + name_int)
    my_inputInt(bot, chat_id, "сколько тебе лет?", dz4_helper2)


def dz4_helper2(bot, chat_id, age_int):
    if 18 > age_int > 10:
        bot.send_message(chat_id, 'какой ты малыш')
    if 18 <= age_int <= 100:
        bot.send_message(chat_id, 'мое уважение, старпер')


# -----------------------------------------------------------------------
def dz5(bot, chat_id):
    my_inputStr(bot, chat_id, "Как тебя зовут?", dz5_helper)


def dz5_helper(bot, chat_id, name_int):
    bot.send_message(chat_id, text="привет " + name_int)
    bot.send_message(chat_id, text=f"\n" f"смотри как могу {name_int[1::-1]},"
                                   f"\n" f"{name_int[::-1]}"
                                   f"\n" f"{name_int[::5]}")


# -----------------------------------------------------------------------
def dz6(bot, chat_id):
    my_inputInt(bot, chat_id, "сколько , будет 2+2*2?", dz6_helper)


def dz6_helper(bot, chat_id, otvet):
    if otvet == 6:
        bot.send_message(chat_id, text="все знают, что ответ будет 8....")
    elif otvet == 8:
        bot.send_message(chat_id, text="молодец")
    else:
        bot.send_message(chat_id, text="тяжелый случай")


# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
def my_input(bot, chat_id, txt, ResponseHandler):
    message = bot.send_message(chat_id, text=txt)
    bot.register_next_step_handler(message, ResponseHandler)
#отключить кнопки на момент ввода!!!!!

# -----------------------------------------------------------------------
def my_inputInt(bot, chat_id, txt, ResponseHandler):
    message = bot.send_message(chat_id, text=txt)
    bot.register_next_step_handler(message, my_inputInt_SecondPart, botQuestion=bot, txtQuestion=txt,
                                   ResponseHandler=ResponseHandler)
    # bot.register_next_step_handler(message, my_inputInt_return, bot, txt, ResponseHandler)  # то-же самое, но короче


def my_inputInt_SecondPart(message, botQuestion, txtQuestion, ResponseHandler):
    chat_id = message.chat.id
    try:
        var_int = int(message.text)
        # данные корректно преобразовались в int, можно вызвать обработчик ответа, и передать туда наше число
        ResponseHandler(botQuestion, chat_id, var_int)
    except ValueError:
        botQuestion.send_message(chat_id,
                                 text="Можно вводить ТОЛЬКО целое число в десятичной системе исчисления (символами от "
                                      "0 до 9)!\nПопробуйте еще раз...")
        my_inputInt(botQuestion, chat_id, txtQuestion, ResponseHandler)  # это не рекурсия, но очень похоже
        # у нас пара процедур, которые вызывают друг-друга, пока пользователь не введёт корректные данные,
        # и тогда этот цикл прервётся, и управление перейдёт "наружу", в ResponseHandler


# -----------------------------------------------------------------------
def my_inputStr(bot, chat_id, txt, ResponseHandler):
    message = bot.send_message(chat_id, text=txt)
    bot.register_next_step_handler(message, my_inputStr_SecondPart, botQuestion=bot, txtQuestion=txt,
                                   ResponseHandler=ResponseHandler)


def my_inputStr_SecondPart(message, botQuestion, txtQuestion, ResponseHandler):
    chat_id = message.chat.id
    var_str = str(message.text)
    if var_str.find(" ") == -1 and var_str.isalpha() == True:
        ResponseHandler(botQuestion, chat_id, var_str)
    else:
        botQuestion.send_message(chat_id, text="введи свое имя без пробелов и цифр")
        my_inputStr(botQuestion, chat_id, txtQuestion, ResponseHandler)
