"""Board, city, and route classes."""

from models.core import CardColor
from models.core import RouteType


class City:
    def __init__(self, name, x=None, y=None):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if other is None:
            return False

        if self.name == other.name:
            return True

        return False

    def __hash__(self):
        return hash(self.name)


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


class BoardMap:
    def __init__(self, map_definition=None):
        self.cities = {}
        self.routes = []
        self.route_scores = {}
        self.layout_size = None

        if map_definition is not None:
            self.route_scores = getattr(map_definition, "route_scores", {}).copy()
            self.layout_size = getattr(map_definition, "layout_size", None)
            city_positions = getattr(map_definition, "city_positions", {})

            for name in map_definition.cities:
                position = city_positions.get(name)

                if position is None:
                    self.cities[name] = City(name)
                else:
                    self.cities[name] = City(name, position.get("x"), position.get("y"))

            route_pairs = {}

            for route_data in map_definition.routes:
                c1 = self.cities[route_data["start"]]
                c2 = self.cities[route_data["end"]]
                route = Route(
                    c1,
                    c2,
                    route_data["color"],
                    route_data["length"],
                    route_data.get("route_type", RouteType.STANDARD),
                    route_data.get("required_locomotives", 0)
                )
                route.visual_points = route_data.get("points", [])
                route.segment_points = route_data.get("segment_points", [])
                self.routes.append(route)

                pair_key = tuple(sorted([c1.name, c2.name]))
                if pair_key in route_pairs:
                    twin = route_pairs[pair_key]
                    route.twin_route = twin
                    twin.twin_route = route
                else:
                    route_pairs[pair_key] = route

    def claimed_routes(self, player):
        claimed = []

        for route in self.routes:
            if route.owner == player:
                claimed.append(route)

        return claimed
