"""Player classes."""


class ScoringMarker:
    def __init__(self):
        self.position = 0

    def move_by(self, points):
        self.position += points


class Player:
    def __init__(self, name, trains_left=17):
        self.name = name
        self.train_cards = []
        self.trains_left = trains_left
        self.score = 0  # Added this so your teammate's scoring logic works
        self.destination_tickets = []
        self.starting_ticket_choices = []
        self.marker = ScoringMarker()

    def take_train_card(self, card):
        if card:
            self.train_cards.append(card)

    def remove_cards(self, cards):
        for card in cards:
            if card in self.train_cards:
                self.train_cards.remove(card)

    def take_tickets(self, new_tickets):
        self.destination_tickets.extend(new_tickets)

    def place_trains(self, count):
        if count <= self.trains_left:
            self.trains_left -= count

    def move_score(self, points):
        self.score += points
        self.marker.move_by(points)

    def __str__(self):
        return f"Player {self.name} | Score: {self.score} | Buses: {self.trains_left}"
