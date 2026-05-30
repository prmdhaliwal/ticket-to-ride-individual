"""Transportation card deck class."""

import random


class TrainCarCardDeck:
    def __init__(self, initial_cards):
        self.deck = initial_cards
        self.discard = []
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def draw_blind(self):
        if not self.deck:
            if not self.discard:
                return None
            self.deck = self.discard
            self.discard = []
            self.shuffle()
        return self.deck.pop()

    def discard_cards(self, cards):
        self.discard.extend(cards)
