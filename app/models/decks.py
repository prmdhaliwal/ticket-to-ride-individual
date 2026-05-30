"""Deck classes."""

import random

from models.core import CardColor


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


class FaceUpPool:
    def __init__(self):
        self.face_up_cards = []

    def refresh(self, deck):
        while len(self.face_up_cards) < 5:
            card = deck.draw_blind()
            if card:
                self.face_up_cards.append(card)
            else:
                break
        self.replace_if_three_buses(deck)

    def draw_face_up(self, index):
        if 0 <= index < len(self.face_up_cards):
            return self.face_up_cards.pop(index)
        return None

    def replace_if_three_buses(self, deck):
        refresh_attempts = 0

        while self.count_buses() >= 3:
            deck.discard_cards(self.face_up_cards)
            self.face_up_cards = []

            while len(self.face_up_cards) < 5:
                card = deck.draw_blind()
                if card:
                    self.face_up_cards.append(card)
                else:
                    break

            refresh_attempts += 1

            if refresh_attempts >= 5:
                break

            if len(self.face_up_cards) < 5:
                break

    def count_buses(self):
        count = 0

        for card in self.face_up_cards:
            if card.colour == CardColor.LOCOMOTIVE:
                count += 1

        return count


class DestinationTicketDeck:
    def __init__(self, initial_tickets):
        self.tickets = initial_tickets
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.tickets)

    def draw(self, count):
        drawn = []
        draw_count = count

        if len(self.tickets) < draw_count:
            draw_count = len(self.tickets)

        for _ in range(draw_count):
            drawn.append(self.tickets.pop())

        return drawn

    def draw_two(self):
        return self.draw(2)

    def draw_three(self):
        return self.draw(3)

    def return_tickets(self, rejected):
        for ticket in rejected:
            self.tickets.insert(0, ticket)
