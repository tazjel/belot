from random import choice

import belot
from interfaces import IPlayer


class PlayerRandom(IPlayer):
    def notifyDeclarations(self, declarations):
        pass

    def notifyTrick(self, cards, value):
        pass

    def notifyHand(self, pointsUs, pointsThem):
        pass

    def notifyBela(self, player, card):
        pass

    def bid(self, must):
        extra=[None]
        if must: extra.pop()

        return choice(belot.suits+extra)

    def playCard(self, table, legalCards):
        return choice(legalCards)

    def declareBela(self, table):
        return choice([True, False])