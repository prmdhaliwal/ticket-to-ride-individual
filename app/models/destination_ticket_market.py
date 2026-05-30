"""Visible destination ticket market."""


class DestinationTicketMarket:
    def __init__(self, market_size=3):
        self.visible_tickets = []
        self.market_size = market_size

    def visible(self):
        return self.visible_tickets

    def refill(self, deck):
        while len(self.visible_tickets) < self.market_size:
            drawn_tickets = deck.draw(1)

            if not drawn_tickets:
                break

            for ticket in drawn_tickets:
                self.visible_tickets.append(ticket)

    def choose_tickets(self, player, kept_tickets, rejected_tickets, deck):
        if len(kept_tickets) < 1:
            return False, "You must keep at least one ticket."

        selected_tickets = []

        for ticket in kept_tickets:
            selected_tickets.append(ticket)

        for ticket in rejected_tickets:
            selected_tickets.append(ticket)

        if len(selected_tickets) != len(self.visible_tickets):
            return False, "Choose what to do with each ticket."

        for ticket in selected_tickets:
            if ticket not in self.visible_tickets:
                return False, "Invalid ticket selection."

        player.take_tickets(kept_tickets)
        self.visible_tickets = []
        self.refill(deck)
        deck.return_tickets(rejected_tickets)

        return True, "Tickets kept."
