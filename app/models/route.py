"""Route class."""

from models.card_color import CardColor
from models.route_type import RouteType


class Route:
    def __init__(
        self,
        city_a,
        city_b,
        colour,
        length,
        route_type=RouteType.STANDARD,
        required_locomotives=0
    ):
        # route connects two cities and starts unclaimed
        self.cities = [city_a, city_b]
        self.city_a = city_a
        self.city_b = city_b
        self.colour = colour
        self.length = length
        self.route_type = route_type
        self.required_locomotives = required_locomotives
        self.owner = None
        self.placed_trains = []
        self.twin_route = None
        self.visual_points = []
        self.segment_points = []

    def claim(self, player):
        self.owner = player

    def is_available(self, total_players_in_game, player=None):
        if self.owner is not None:
            return False

        if self.twin_route is not None:
            if player is not None and self.twin_route.owner == player:
                return False

            if total_players_in_game == 2 and self.twin_route.owner is not None:
                return False

        return True

    def can_accept(self, cards):
        if len(cards) != self.length:
            return False

        if self.colour == CardColor.GRAY:
            colours_used = []

            for card in cards:
                if card.colour != CardColor.LOCOMOTIVE:
                    if card.colour not in colours_used:
                        colours_used.append(card.colour)

            if len(colours_used) <= 1:
                return True

            return False

        for card in cards:
            if not card.matches(self.colour):
                return False

        return True

    def points(self, score_table):
        if self.length in score_table:
            return score_table[self.length]

        return 0
