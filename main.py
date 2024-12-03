from cmu_graphics import *
import random
import textwrap
import datetime
CARD_COLORS = ['DeepSkyBlue', 'ForestGreen', 'Tomato', 'SlateGray']
CARD_NUMBERS = list(range(0, 10))
SPECIAL_CARDS = ['+2', 'skip', 'reverse']
class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    def isPlayable(self, currentCard):
        return (
            self.color == 'wild' or
            self.color == currentCard.color or
            self.value == currentCard.value
        )
    def draw(self, x, y, highlight=False, large=False):
        fillColor = self.color if self.color in CARD_COLORS else 'gray'
        width, height = (120, 180) if large else (80, 120)
        drawRect(x, y, width, height, fill=fillColor, border='black', borderWidth=2)
        labelText = str(self.value).upper() if self.color == 'wild' else str(self.value)
        textColor = 'white' if fillColor != 'yellow' else 'black'
        drawLabel(
            labelText,
            x + width / 2,
            y + height / 2,
            size=20 if large else 15,
            fill=textColor,
            align='center'
        )
        if highlight:
            drawRect(
                x - 5,
                y - 5,
                width + 10,
                height + 10,
                fill=None,
                border='gold',
                borderWidth=3
            )
        if not large:
            labelType = (
                "Special" if self.value in SPECIAL_CARDS
                else "Number" if isinstance(self.value, int)
                else "Wild"
            )
            drawLabel(
                labelType,
                x + width / 2,
                y + height - 10,
                size=12,
                fill='black',
                align='center'
            )
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
    def drawCard(self, deck):
        if deck:
            self.hand.append(deck.pop())
    def playCard(self, index):
        return self.hand.pop(index)
class UnoGame:
    def __init__(self):
        self.deck = self.createDeck()
        self.currentCard = self.drawStartingCard()
        self.players = [Player("Player 1"), Player("Player 2")]
        self.currentPlayerIndex = 0
        self.winner = None
        self.messageLog = ["Welcome to UNO!"]
        self.turnMessage = ""
        self.turnDelayPhase = None
        self.turnDelayEndTime = None
        self.countdown = 0
        self.reverse = False
        self.colorChange = False
        self.currentColorChoice = None
        self.lastAction = ""
        self.popupVisible = False
        self.next_player_skip = False
        for player in self.players:
            for _ in range(7):
                player.drawCard(self.deck)
    def createDeck(self):
        deck = []
        for color in CARD_COLORS:
            for number in CARD_NUMBERS:
                deck.append(Card(color, number))
            for special in SPECIAL_CARDS:
                deck.append(Card(color, special))
        for _ in range(4):
            deck.append(Card('wild', '+4'))
        random.shuffle(deck)
        return deck
    def drawStartingCard(self):
        while self.deck:
            card = self.deck.pop()
            if card.color != 'wild':
                return card
        return Card('red', 0)
    def nextPlayer(self):
        if self.reverse:
            self.currentPlayerIndex = (self.currentPlayerIndex - 1) % len(self.players)
        else:
            self.currentPlayerIndex = (self.currentPlayerIndex + 1) % len(self.players)
    def logMessage(self, message):
        separator = "----------------------------"
        wrappedMessage = textwrap.wrap(message, width=40)
        logEntry = wrappedMessage + [separator]
        self.messageLog = logEntry + self.messageLog[:10 - len(logEntry)]
    def handleSpecialCard(self, card):
        action_taken = ""
        if card.value in ['skip', 'reverse']:
            action = 'skip' if card.value == 'reverse' else card.value
            self.logMessage(f"{self.players[self.currentPlayerIndex].name} was skipped!")
            action_taken = f"{self.players[self.currentPlayerIndex].name} was skipped!"
            self.next_player_skip = True
            self.startPreTransitionDelay(action_taken)
        elif card.value == '+2':
            next_player = (self.currentPlayerIndex + 1) % len(self.players)
            self.logMessage(f"{self.players[next_player].name} draws 2 cards!")
            action_taken = f"{self.players[next_player].name} draws 2 cards!"
            for _ in range(2):
                self.players[next_player].drawCard(self.deck)
            self.next_player_skip = True
            self.startPreTransitionDelay(action_taken)
        elif card.value == '+4':
            next_player = (self.currentPlayerIndex + 1) % len(self.players)
            self.logMessage(f"{self.players[next_player].name} draws 4 cards and {self.players[self.currentPlayerIndex].name} changes color!")
            action_taken = f"{self.players[next_player].name} draws 4 cards and {self.players[self.currentPlayerIndex].name} changes color!"
            for _ in range(4):
                self.players[next_player].drawCard(self.deck)
            self.colorChange = True
            self.next_player_skip = True
            self.startPreTransitionDelay(action_taken)
        self.lastAction = action_taken
    def startPreTransitionDelay(self, action):
        self.turnDelayPhase = 'pre-transition'
        self.turnDelayEndTime = datetime.datetime.now() + datetime.timedelta(seconds=0)
        self.lastAction = action
    def startTransitionDelay(self):
        self.turnDelayPhase = 'transition'
        self.turnDelayEndTime = datetime.datetime.now() + datetime.timedelta(seconds=8)
        self.countdown = 8
    def updateCountdown(self):
        current_time = datetime.datetime.now()
        if self.turnDelayPhase == 'transition':
            remaining = self.turnDelayEndTime - current_time
            self.countdown = max(int(remaining.total_seconds()), 0)
            if remaining.total_seconds() <= 0:
                self.turnDelayPhase = None
                self.turnMessage = ""
                self.lastAction = ""
                self.countdown = 0
                if not self.next_player_skip:
                    self.nextPlayer()
                else:
                    self.next_player_skip = False
        elif self.turnDelayPhase == 'pre-transition':
            remaining = self.turnDelayEndTime - current_time
            if remaining.total_seconds() <= 0:
                self.startTransitionDelay()
    def drawGame(self, app):
        drawRect(0, 0, app.width, app.height, fill='lightblue')
        if self.winner:
            drawRect(0, 0, app.width, app.height, fill='black', opacity=70)
            popup_width, popup_height = 400, 200
            popup_x = (app.width - popup_width) / 2
            popup_y = (app.height - popup_height) / 2
            drawRect(popup_x, popup_y, popup_width, popup_height, fill='white', border='black', borderWidth=2)
            drawLabel(
                f"{self.winner.name} Wins!",
                app.width / 2,
                popup_y + 60,
                size=24,
                fill='black',
                align='center'
            )
            button_width, button_height = 100, 40
            button_x = app.width / 2 - button_width / 2
            button_y = popup_y + 130
            drawRect(button_x, button_y, button_width, button_height, fill='green', border='black', borderWidth=2)
            drawLabel(
                "Reset",
                app.width / 2,
                button_y + button_height / 2,
                size=18,
                fill='white',
                align='center'
            )
            return
        if self.turnDelayPhase == 'transition':
            drawRect(0, 0, app.width, app.height, fill='black', opacity=80)
            drawLabel(self.turnMessage, app.width / 2, app.height / 2 - 30, size=24, fill='white', align='center')
            if self.lastAction:
                drawLabel(
                    f"Action: {self.lastAction}",
                    app.width / 2,
                    app.height / 2 + 10,
                    size=25,
                    fill='white',
                    align='center'
                )
            drawLabel(f"Next turn in: {self.countdown}", app.width / 2, app.height / 2 + 50, size=25, fill='white', align='center')
            return
        drawRect(0, 0, 300, app.height, fill='beige', border='black', borderWidth=2)
        drawLabel("--Messages Log--", 150, 20, size=20, fill='black')
        for i, message in enumerate(self.messageLog):
            if i >= 10:
                break
            drawLabel(message, 10, 60 + i * 20, size=15, fill='black', align='left')
        drawLabel("Card to Follow", app.width / 2 - 8, 20, size=25, fill='black')
        self.currentCard.draw(app.width / 2 - 60, 70, large=True)
        drawRect(app.width / 2 + 400, 100, 80, 120, fill='gray', border='black', borderWidth=2)
        drawLabel("Deck", app.width / 2 + 440, 160, size=18, fill='black')
        for i, player in enumerate(self.players):
            yOffset = app.height - 220 if i == 0 else 350
            grey_out = (i != self.currentPlayerIndex) and (self.turnDelayPhase is None)
            for j, card in enumerate(player.hand):
                cardXStart = 320 + j * 90
                if grey_out:
                    drawRect(cardXStart, yOffset, 80, 120, fill='black')
                    drawLabel(
                        "UNO",
                        cardXStart + 40,
                        yOffset + 60,
                        size=20,
                        fill='white',
                        align='center'
                    )
                else:
                    highlight = i == self.currentPlayerIndex and not self.colorChange
                    card.draw(cardXStart, yOffset, highlight=highlight)
        drawRect(0, app.height - 80, app.width, 80, fill='beige', border='black', borderWidth=2)
        drawLabel(
            f"Current Player: {self.players[self.currentPlayerIndex].name} | Cards Left: {self.players[0].name} ({len(self.players[0].hand)}), {self.players[1].name} ({len(self.players[1].hand)})",
            app.width / 2,
            app.height - 60,
            size=25,
            fill='black'
        )
        if self.colorChange:
            self.showColorPicker(app)
    def showColorPicker(self, app):
        colors = ['red', 'green', 'blue', 'yellow']
        for i, color in enumerate(colors):
            rect_y = 300 + i * 50
            drawRect(app.width - 150, rect_y, 100, 40, fill=color, border='black', borderWidth=2)
            textColor = 'white' if color != 'yellow' else 'black'
            drawLabel(
                f"Pick {color}",
                app.width - 100,
                rect_y + 20,
                size=15,
                fill=textColor,
                align='center'
            )
    def handleMousePress(self, app, x, y):
        if self.winner:
            popup_width, popup_height = 400, 200
            popup_x = (app.width - popup_width) / 2
            popup_y = (app.height - popup_height) / 2
            button_width, button_height = 100, 40
            button_x = app.width / 2 - button_width / 2
            button_y = popup_y + 130
            if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                self.resetGame()
            return
        if self.colorChange:
            if app.width - 150 <= x <= app.width - 50:
                if 300 <= y <= 340:
                    self.currentColorChoice = 'red'
                elif 350 <= y <= 390:
                    self.currentColorChoice = 'green'
                elif 400 <= y <= 440:
                    self.currentColorChoice = 'blue'
                elif 450 <= y <= 490:
                    self.currentColorChoice = 'yellow'
                if self.currentColorChoice:
                    self.currentCard.color = self.currentColorChoice
                    self.colorChange = False
                    self.logMessage(f"{self.players[self.currentPlayerIndex].name} changed color to {self.currentColorChoice}.")
                    action_taken = f"{self.players[self.currentPlayerIndex].name} changed color to {self.currentColorChoice}."
                    self.startPreTransitionDelay(action_taken)
            return
        if app.width / 2 + 400 <= x <= app.width / 2 + 480 and 100 <= y <= 220:
            player = self.players[self.currentPlayerIndex]
            if not self.turnDelayPhase and not self.colorChange:
                player.drawCard(self.deck)
                self.logMessage(f"{player.name} drew a card.")
                action_taken = f"{player.name} drew a card."
                self.startPreTransitionDelay(action_taken)
            return
        if not self.turnDelayPhase and not self.colorChange:
            active_player = self.players[self.currentPlayerIndex]
            if self.currentPlayerIndex == 0:
                cardYStart = app.height - 220
            else:
                cardYStart = 350
            cardYEnd = cardYStart + 120
            for i, card in enumerate(active_player.hand):
                cardXStart = 320 + i * 90
                cardXEnd = cardXStart + 80
                if cardXStart <= x <= cardXEnd and cardYStart <= y <= cardYEnd:
                    if card.isPlayable(self.currentCard):
                        self.currentCard = active_player.playCard(i)
                        self.logMessage(f"{active_player.name} played {card.color} {card.value}.")
                        action_taken = f"{active_player.name} played {card.color} {card.value}."
                        self.handleSpecialCard(card)
                        if len(active_player.hand) == 0:
                            self.winner = active_player
                            self.logMessage(f"{active_player.name} wins! Game Over!")
                        else:
                            if not self.colorChange:
                                self.startPreTransitionDelay(action_taken)
                    else:
                        self.logMessage("Card not playable. Try again.")
                    return
    def resetGame(self):
            self.deck = self.createDeck()
            self.currentCard = self.drawStartingCard()
            self.currentPlayerIndex = 0
            self.winner = None
            self.messageLog = ["Welcome to UNO!"]
            self.turnMessage = ""
            self.turnDelayPhase = None
            self.turnDelayEndTime = None
            self.countdown = 0
            self.reverse = False
            self.colorChange = False
            self.currentColorChoice = None
            self.lastAction = ""
            self.popupVisible = False
            self.next_player_skip = False
            for player in self.players:
                player.hand = []
                for _ in range(7):
                    player.drawCard(self.deck)
def onStep(app):
        game.updateCountdown()
def onAppStart(app):
        app.width = 1400
        app.height = 900
def redrawAll(app):
        game.drawGame(app)
def onMousePress(app, x, y):
        game.handleMousePress(app, x, y)
game = UnoGame()
runApp(
        width=1400,
        height=900
    )
