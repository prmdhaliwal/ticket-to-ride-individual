"""Destination ticket deck class."""

import random


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
