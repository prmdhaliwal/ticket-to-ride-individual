"""Standard route claiming rules."""

from models.core import CardColor
from models.route_claim_strategy import RouteClaimStrategy


class StandardRouteClaimStrategy(RouteClaimStrategy):
    def can_claim(self, player, route):
        if player.trains_left < route.length:
            return False, "Not enough bus pieces.", []

        cards_to_use = self.choose_cards_for_route(player, route)
        if len(cards_to_use) < route.length:
            return False, "Not enough matching transportation cards.", []

        return True, "Route claimed.", cards_to_use

    def matching_cards(self, player, route_colour):
        matching = []

        for card in player.train_cards:
            if card.matches(route_colour):
                matching.append(card)

        return matching

    def choose_cards_for_route(self, player, route):
        if route.colour == CardColor.GRAY:
            return self.choose_cards_for_gray_route(player, route)

        matching_cards = self.matching_cards(player, route.colour)
        coloured_cards = []
        locomotive_cards = []

        for card in matching_cards:
            if card.colour == CardColor.LOCOMOTIVE:
                locomotive_cards.append(card)
            else:
                coloured_cards.append(card)

        cards_to_use = []

        for card in coloured_cards:
            if len(cards_to_use) < route.length:
                cards_to_use.append(card)

        for card in locomotive_cards:
            if len(cards_to_use) < route.length:
                cards_to_use.append(card)

        if self.can_claim_route(route, cards_to_use):
            return cards_to_use

        return []

    def choose_cards_for_gray_route(self, player, route):
        wild_cards = []
        cards_by_colour = {}

        for card in player.train_cards:
            if card.colour == CardColor.LOCOMOTIVE:
                wild_cards.append(card)
            else:
                if card.colour not in cards_by_colour:
                    cards_by_colour[card.colour] = []

                cards_by_colour[card.colour].append(card)

        sorted_colours = self.sort_colours_by_card_count(cards_by_colour)

        for colour in sorted_colours:
            cards_to_use = []

            for card in cards_by_colour[colour]:
                if len(cards_to_use) < route.length:
                    cards_to_use.append(card)

            for card in wild_cards:
                if len(cards_to_use) < route.length:
                    cards_to_use.append(card)

            if self.can_claim_route(route, cards_to_use):
                return cards_to_use

        cards_to_use = []

        for card in wild_cards:
            if len(cards_to_use) < route.length:
                cards_to_use.append(card)

        if self.can_claim_route(route, cards_to_use):
            return cards_to_use

        return []

    def sort_colours_by_card_count(self, cards_by_colour):
        remaining_colours = []
        sorted_colours = []

        for colour in cards_by_colour:
            remaining_colours.append(colour)

        while remaining_colours:
            best_colour = None
            best_count = -1

            for colour in remaining_colours:
                card_count = len(cards_by_colour[colour])

                if card_count > best_count:
                    best_colour = colour
                    best_count = card_count

            sorted_colours.append(best_colour)
            remaining_colours.remove(best_colour)

        return sorted_colours

    def can_claim_route(self, route, cards):
        return route.can_accept(cards)
