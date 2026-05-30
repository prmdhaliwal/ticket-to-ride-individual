"""Face-up transportation card pool class."""

from models.card_color import CardColor


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
