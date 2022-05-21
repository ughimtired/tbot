import threading

import requests
from telebot import types
import menuBot

# -----------------------------------------------------------------------
# вместо того, что бы делать еще один класс, обойдёмся без него - подумайте, почему и как
activeGames = {}  # Тут будем накапливать все активные игры. У пользователя может быть только одна активная игра


def newGame(chatID, newGame):
    activeGames.update({chatID: newGame})
    return newGame


def getGame(chatID):
    return activeGames.get(chatID, None)


def stopGame(chatID):
    activeGames.pop(chatID, None)


# def looper(classGame):
#     if classGame.gameTimeLeft > 0:
#         classGame.gameTimeLeft -= 1
#         # print(classGame.gameTimeLeft)
#         classGame.setTextGame()
#         threading.Timer(1, looper, args=[classGame]).start()
#

# -----------------------------------------------------------------------
class Card:
    emo_SPADES = "U0002660"  # Unicod эмоджи Пики
    emo_CLUBS = "U0002663"  # Unicod эмоджи Крести
    emo_HEARTS = "U0002665"  # Unicod эмоджи Черви
    emo_DIAMONDS = "U0002666"  # Unicod эмоджи Буби

    def __init__(self, card):
        if isinstance(card, dict):  # если передали словарь
            self.__card_JSON = card
            self.code = card["code"]
            self.suit = card["suit"]
            self.value = card["value"]
            self.cost = self.get_cost_card()
            self.color = self.get_color_card()
            self.__imagesPNG_URL = card["images"]["png"]
            self.__imagesSVG_URL = card["images"]["svg"]
            # print(self.value, self.suit, self.code)

        elif isinstance(card, str):  # карту передали строкой, в формате "2S"
            self.__card_JSON = None
            self.code = card

            value = card[0]
            if value == "0":
                self.value = "10"
            elif value == "J":
                self.value = "JACK"
            elif value == "Q":
                self.value = "QUEEN"
            elif value == "K":
                self.value = "KING"
            elif value == "A":
                self.value = "ACE"
            elif value == "X":
                self.value = "JOKER"
            else:
                self.value = value

            suit = card[1]
            if suit == "1":
                self.suit = ""
                self.color = "BLACK"

            elif suit == "2":
                self.suit = ""
                self.color = "RED"

            else:
                if suit == "S":
                    self.suit = "SPADES"  # Пики
                elif suit == "C":
                    self.suit = "CLUBS"  # Крести
                elif suit == "H":
                    self.suit = "HEARTS"  # Черви
                elif suit == "D":
                    self.suit = "DIAMONDS"  # Буби

                self.cost = self.get_cost_card()
                self.color = self.get_color_card()

    def get_cost_card(self):
        if self.value == "JACK":
            return 2
        elif self.value == "QUEEN":
            return 3
        elif self.value == "KING":
            return 4
        elif self.value == "ACE":
            return 11
        elif self.value == "JOKER":
            return 1
        else:
            return int(self.value)

    def get_color_card(self):
        if self.suit == "SPADES":  # Пики
            return "BLACK"
        elif self.suit == "CLUBS":  # Крести
            return "BLACK"
        elif self.suit == "HEARTS":  # Черви
            return "RED"
        elif self.suit == "DIAMONDS":  # Буби
            return "RED"


# -----------------------------------------------------------------------
class GameMoreLess:
    values = ["Больше", "Меньше", "Равно"]

    def __init__(self, deck_count=1, jokers_enabled=False):
        new_pack = self.new_pack(deck_count, jokers_enabled)  # в конструкторе создаём новую пачку из deck_count-колод
        self.previous_card = None
        if new_pack is not None:
            self.pack_card = new_pack  # сформированная колода
            self.remaining = new_pack["remaining"],  # количество оставшихся карт в колоде
            self.card_in_game = []  # карты в игре
            self.arr_cards_URL = []  # URL карт игрока
            self.score = 0  # очки игрока
            self.status = None  # статус игры, True - игрок выиграл, False - Игрок проиграл, None - Игра продолжается

    def new_pack(self, deck_count, jokers_enabled=False):
        txtJoker = "&jokers_enabled=true" if jokers_enabled else ""
        response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}" + txtJoker)
        # создание стопки карт из "deck_count" колод по 52 карты
        if response.status_code != 200:
            return None
        pack_card = response.json()
        return pack_card

    def cardCost(self, card_value):
        if card_value == "JACK":
            card_cost = 11
        elif card_value == "QUEEN":
            card_cost = 12
        elif card_value == "KING":
            card_cost = 13
        elif card_value == "ACE":
            card_cost = 14
        elif card_value == "JOCKER":
            card_cost = 15
        else:
            card_cost = int(card_value)

        return card_cost

    def playerChoice(self, player1Choice, card_value):
        nowCard = self.cardCost(card_value)
        previousCard = self.cardCost(self.previous_card)
        if player1Choice == "Больше" and previousCard < nowCard:
            return 1
        elif player1Choice == "Меньше" and previousCard > nowCard:
            return 1
        elif player1Choice == "Равно" and previousCard == nowCard:
            return 1
        else:
            return 0

    def get_cards(self, card_count=1, choice=None):
        if self.pack_card is None:
            return None
        if self.status is not None:  # игра закончена
            return None

        deck_id = self.pack_card["deck_id"]
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={card_count}")

        if response.status_code != 200:
            return False

        new_cards = response.json()
        if not new_cards["success"]:
            return False

        self.remaining = new_cards["remaining"]  # обновим в классе количество оставшихся карт в колоде
        arr_newCards = []
        for card in new_cards["cards"]:
            card_obj = Card(card)  # создаем объекты класса Card и добавляем их в список карт у игрока
            arr_newCards.append(card_obj)
            self.card_in_game.append(card_obj)
            if self.previous_card is not None:
                self.score += self.playerChoice(choice, card_obj.value)  # self.score + card_obj.cost
            self.previous_card = card_obj.value
            if len(self.arr_cards_URL) == 0:
                self.arr_cards_URL.append(card["image"])
            else:
                self.arr_cards_URL.pop()
                self.arr_cards_URL.append(card["image"])

        text_game = "Ваш счет: " + str(self.score) + " в колоде осталось карт: " + str(self.remaining)

        return text_game


# ---------------------------------------------------------------------
class Game21:
    def __init__(self, deck_count=1, jokers_enabled=False):
        new_pack = self.new_pack(deck_count, jokers_enabled)  # в конструкторе создаём новую пачку из deck_count-колод
        if new_pack is not None:
            self.pack_card = new_pack  # сформированная колода
            self.remaining = new_pack["remaining"],  # количество оставшихся карт в колоде
            self.card_in_game = []  # карты в игре
            self.arr_cards_URL = []  # URL карт игрока
            self.score = 0  # очки игрока
            self.status = None  # статус игры, True - игрок выиграл, False - Игрок проиграл, None - Игра продолжается

    # ---------------------------------------------------------------------
    def new_pack(self, deck_count, jokers_enabled=False):
        txtJoker = "&jokers_enabled=true" if jokers_enabled else ""
        response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}" + txtJoker)
        # создание стопки карт из "deck_count" колод по 52 карты
        if response.status_code != 200:
            return None
        pack_card = response.json()
        return pack_card

    # ---------------------------------------------------------------------
    def get_cards(self, card_count=1):
        if self.pack_card is None:
            return None
        if self.status is not None:  # игра закончена
            return None

        deck_id = self.pack_card["deck_id"]
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={card_count}")
        # достать из deck_id-колоды card_count-карт
        if response.status_code != 200:
            return False

        new_cards = response.json()
        if not new_cards["success"]:
            return False
        self.remaining = new_cards["remaining"]  # обновим в классе количество оставшихся карт в колоде

        arr_newCards = []
        for card in new_cards["cards"]:
            card_obj = Card(card)  # создаем объекты класса Card и добавляем их в список карт у игрока
            arr_newCards.append(card_obj)
            self.card_in_game.append(card_obj)
            self.score = self.score + card_obj.cost
            self.arr_cards_URL.append(card["image"])

        if self.score > 21:
            self.status = False
            text_game = "Очков: " + str(self.score) + " ВЫ ПРОИГРАЛИ!"

        elif self.score == 21:
            self.status = True
            text_game = "ВЫ ВЫИГРАЛИ!"
        else:
            self.status = None
            text_game = "Очков: " + str(self.score) + " в колоде осталось карт: " + str(self.remaining)

        return text_game


# ------------------------------------------------------------------------------
class GameMoreLess:
    values = ["Больше", "Меньше", "Равно"]

    def __init__(self, deck_count=1, jokers_enabled=False):
        new_pack = self.new_pack(deck_count, jokers_enabled)  # в конструкторе создаём новую пачку из deck_count-колод
        self.previous_card = None
        if new_pack is not None:
            self.life = 3
            self.pack_card = new_pack  # сформированная колода
            self.remaining = new_pack["remaining"],  # количество оставшихся карт в колоде
            self.card_in_game = []  # карты в игре
            self.arr_cards_URL = []  # URL карт игрока
            self.score = 0  # очки игрока
            self.status = None  # статус игры, True - игрок выиграл, False - Игрок проиграл, None - Игра продолжается

    def new_pack(self, deck_count, jokers_enabled=False):
        txtJoker = "&jokers_enabled=true" if jokers_enabled else ""
        response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}" + txtJoker)
        # создание стопки карт из "deck_count" колод по 52 карты
        if response.status_code != 200:
            return None
        pack_card = response.json()
        return pack_card

    def cardCost(self, card_value):
        if card_value == "JACK":
            card_cost = 11
        elif card_value == "QUEEN":
            card_cost = 12
        elif card_value == "KING":
            card_cost = 13
        elif card_value == "ACE":
            card_cost = 14
        elif card_value == "JOCKER":
            card_cost = 15
        else:
            card_cost = int(card_value)

        return card_cost

    def playerChoice(self, player1Choice, card_value):
        nowCard = self.cardCost(card_value)
        previousCard = self.cardCost(self.previous_card)
        if player1Choice == "Больше" and previousCard < nowCard:
            return 1
        elif player1Choice == "Меньше" and previousCard > nowCard:
            return 1
        elif player1Choice == "Равно" and previousCard == nowCard:
            return 1
        else:
            return 0


    def get_cards(self, card_count=1, choice=None):
        if self.pack_card is None:
            return None
        if self.status is not None:  # игра закончена
            return None

        deck_id = self.pack_card["deck_id"]
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={card_count}")

        if response.status_code != 200:
            return False

        new_cards = response.json()
        if not new_cards["success"]:
            return False

        self.remaining = new_cards["remaining"]  # обновим в классе количество оставшихся карт в колоде
        arr_newCards = []
        for card in new_cards["cards"]:
            card_obj = Card(card)  # создаем объекты класса Card и добавляем их в список карт у игрока
            arr_newCards.append(card_obj)
            self.card_in_game.append(card_obj)
            if self.previous_card is not None:
                self.score += self.playerChoice(choice, card_obj.value)  # self.score + card_obj.cost
                if self.playerChoice(choice, card_obj.value) == 0:
                    self.life -= 1
            self.previous_card = card_obj.value
            if len(self.arr_cards_URL) == 0:
                self.arr_cards_URL.append(card["image"])
            else:
                self.arr_cards_URL.pop()
                self.arr_cards_URL.append(card["image"])

        if self.score<52 and self.life != 0:
            text_game = "ваш счет: " + str(self.score) + " в колоде осталось карт: " + str(self.remaining) + " кол-во оставшихся попыток: " + str(self.life)
        elif self.life == 0:
            self.status = False
            text_game = "ПРОИГРЫШ"
        else:
            self.status = False
            text_game = "ПОБЕДА"

        return text_game


# ------------------------------------------------------------------------------
# -----------------------------------------------------------------------
class GameRPS:
    values = ["Камень", "Ножницы", "Бумага"]

    def __init__(self):
        self.computerChoice = self.__class__.getRandomChoice()

    def newGame(self):
        self.computerChoice = self.__class__.getRandomChoice()

    @classmethod
    def getRandomChoice(cls):
        lenValues = len(cls.values)
        import random
        rndInd = random.randint(0, lenValues - 1)
        return cls.values[rndInd]

    def playerChoice(self, player1Choice):
        winner = None

        code = player1Choice[0] + self.computerChoice[0]
        if player1Choice == self.computerChoice:
            winner = "Ничья!"
        elif code == "КН" or code == "БК" or code == "НБ":
            winner = "Игрок выиграл!"
        else:
            winner = "Компьютер выиграл!"

        return f"{player1Choice} vs {self.computerChoice} = " + winner


# -----------------------------------------------------------------------
class GameRPS_Multiplayer:
    game_duration = 10  # сек.
    values = ["Камень", "Ножницы", "Бумага"]
    name = "Игра Камень-Ножницы-Бумага (Мультиплеер)"
    text_rules = "<b>Победитель определяется по следующим правилам:</b>\n" \
                 "1. Камень побеждает ножницы\n" \
                 "2. Бумага побеждает камень\n" \
                 "3. Ножницы побеждают бумагу\n" \
                 "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
    url_picRules = "https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg"

    class Player:

        def __init__(self, playerID, playerName):
            self.id = playerID
            self.gameMessage = None
            self.name = playerName
            self.scores = 0
            self.choice = None
            self.lastChoice = ""

        def __str__(self):
            return self.name

    def __init__(self, bot, chat_user):
        self.id = chat_user.id
        self.gameNumber = 1  # счётчик сыгранных игр
        self.objBot = bot
        self.players = {}
        self.gameTimeLeft = 0
        self.objTimer = None
        self.winner = None
        self.lastWinner = None
        self.textGame = ""
        self.addPlayer(None, "Компьютер")
        self.addPlayer(chat_user.id, chat_user.userName)

    def addPlayer(self, playerID, playerName):
        newPlayer = self.Player(playerID, playerName)
        self.players[playerID] = newPlayer
        if playerID is not None:  # None - это компьютер
            self.startTimer()  # при присоединении нового игрока перезапустим таймер
            self.setTextGame()
            # создадим в чате пользователя игровое сообщение с кнопками, и сохраним его для последующего редактирования
            url_picRules = self.url_picRules
            keyboard = types.InlineKeyboardMarkup()
            list_btn = []
            for keyName in self.values:
                list_btn.append(types.InlineKeyboardButton(text=keyName,
                                                           callback_data="GameRPSm|Choice-" + keyName + "|" + menuBot.Menu.setExtPar(
                                                               self)))
            keyboard.add(*list_btn)
            list_btn = types.InlineKeyboardButton(text="Выход",
                                                  callback_data="GameRPSm|Exit|" + menuBot.Menu.setExtPar(self))
            keyboard.add(list_btn)
            gameMessage = self.objBot.send_photo(playerID, photo=url_picRules, caption=self.textGame, parse_mode='HTML',
                                                 reply_markup=keyboard)
            self.players[playerID].gameMessage = gameMessage
        else:
            newPlayer.choice = self.__class__.getRandomChoice()
        self.sendMessagesAllPlayers([playerID])  # отправим всем остальным игрокам информацию о новом игроке
        return newPlayer

    def delPlayer(self, playerID):
        print("DEL")
        remotePlayer = self.players.pop(playerID)
        try:
            self.objBot.delete_message(chat_id=remotePlayer.id, message_id=remotePlayer.gameMessage.id)
        except:
            pass
        self.objBot.send_message(chat_id=remotePlayer.id, text="Мне жаль, вас выкинуло из игры!")
        menuBot.goto_menu(self.objBot, remotePlayer.id, "Игры")
        self.findWiner()  # как только игрок выходит, проверим среди оставшихся есть ли победитель
        if len(self.players.values()) == 1:
            stopGame(self.id)

    def getPlayer(self, chat_userID):
        return self.players.get(chat_userID)

    def newGame(self):
        self.gameNumber += 1
        self.lastWinner = self.winner
        self.winner = None
        for player in self.players.values():
            player.lastChoice = player.choice
            if player.id == None:  # это компьютер
                player.choice = self.__class__.getRandomChoice()
            else:
                player.choice = None
        self.startTimer()  # запустим таймер игры (если таймер активен, сбросим его)

    def looper(self):
        print("LOOP", self.objTimer)
        if self.gameTimeLeft > 0:
            self.setTextGame()
            self.sendMessagesAllPlayers()
            self.gameTimeLeft -= 1
            self.objTimer = threading.Timer(1, self.looper)
            self.objTimer.start()
            print(self.objTimer.name, self.gameTimeLeft)
        else:
            delList = []
            for player in self.players.values():
                if player.choice is None:
                    delList.append(player.id)
            for idPlayer in delList:
                self.delPlayer(idPlayer)

    def startTimer(self):
        print("START")
        self.stopTimer()
        self.gameTimeLeft = self.game_duration
        self.looper()

    def stopTimer(self):
        print("STOP")
        self.gameTimeLeft = 0
        if self.objTimer is not None:
            self.objTimer.cancel()
            self.objTimer = None

    @classmethod
    def getRandomChoice(cls):
        import random
        # lenValues = len(cls.values)
        # rndInd = random.randint(0, lenValues-1)
        # return cls.values[rndInd]
        return random.choice(cls.values)

    def checkEndGame(self):
        isEndGame = True
        for player in self.players.values():
            isEndGame = isEndGame and player.choice != None
        return isEndGame

    def playerChoice(self, chat_userID, сhoice):
        player = self.getPlayer(chat_userID)
        player.choice = сhoice
        self.findWiner()
        self.sendMessagesAllPlayers()

    def findWiner(self):
        if self.checkEndGame():
            self.stopTimer()  # все успели сделать ход, таймер выключаем
            playersChoice = []
            for player in self.players.values():
                playersChoice.append(player.choice)
            choices = dict(zip(playersChoice, [playersChoice.count(i) for i in playersChoice]))
            if len(choices) == 1 or len(choices) == len(self.__class__.values):
                # если все выбрали одно значение, или если присутствуют все возможные варианты - это ничья
                self.winner = "Ничья"
            else:
                # к этому моменту останется всего два варианта, надо понять есть ли уникальный он и бьёт ли он других
                choice1, quantity1 = choices.popitem()
                choice2, quantity2 = choices.popitem()

                code = choice1[0] + choice2[0]
                if quantity1 == 1 and code == "КН" or code == "БК" or code == "НБ":
                    choiceWiner = choice1
                elif quantity2 == 1 and code == "НК" or code == "КБ" or code == "БН":
                    choiceWiner = choice2
                else:
                    choiceWiner = None

                if choiceWiner != None:
                    winner = ""
                    for player in self.players.values():
                        if player.choice == choiceWiner:
                            winner = player
                            winner.scores += 1
                            break
                    self.winner = winner

                else:
                    self.winner = "Ничья"
        self.setTextGame()

        if self.checkEndGame() and len(self.players) > 1:  # начинаем новую партию через 3 секунды
            self.objTimer = threading.Timer(3, self.newGame)
            self.objTimer.start()

    def setTextGame(self):
        from prettytable import PrettyTable
        mytable = PrettyTable()
        mytable.field_names = ["Игрок", "Счёт", "Выбор", "Результат"]  # имена полей таблицы
        for player in self.players.values():
            mytable.add_row(
                [player.name, player.scores, player.lastChoice, "Победитель!" if self.lastWinner == player else ""])

        textGame = self.text_rules + "\n\n"
        textGame += "<code>" + mytable.get_string() + "</code>" + "\n\n"

        if self.winner is None:
            textGame += f"Идёт игра... <b>Осталось времени для выбора: {self.gameTimeLeft}</b>\n"
        elif self.winner == "Ничья":
            textGame += f"<b>Ничья!</b> Пауза 3 секунды..."
        else:
            textGame += f"Выиграл: <b>{self.winner}! Пауза 3 секунды..."

        self.textGame = textGame

    def sendMessagesAllPlayers(self, excludingPlayers=()):
        try:
            for player in self.players.values():
                if player.id is not None and player.id not in excludingPlayers:
                    textIndividual = f"\n Ваш выбор: {player.choice}, ждём остальных!" if player.choice is not None else "\n"
                    self.objBot.edit_message_caption(chat_id=player.id, message_id=player.gameMessage.id,
                                                     caption=self.textGame + textIndividual, parse_mode='HTML',
                                                     reply_markup=player.gameMessage.reply_markup)
        except:
            pass


# -----------------------------------------------------------------------
if __name__ == "__main__":
    print("Этот код должен использоваться ТОЛЬКО в качестве модуля!")
