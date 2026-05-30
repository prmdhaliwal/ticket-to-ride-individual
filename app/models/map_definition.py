"""Map definition data."""

from models.core import RouteType


class MapDefinition:
    def __init__(
        self,
        map_name,
        min_players,
        max_players,
        initial_train_pieces,
        route_scores=None
    ):
        self.map_name = map_name
        self.min_players = min_players
        self.max_players = max_players
        self.initial_train_pieces = initial_train_pieces

        self.cities = []
        self.city_positions = {}
        self.routes = []
        self.tickets = []
        self.layout_size = None
        self.route_scores = {}

        if route_scores is not None:
            for route_length in route_scores:
                self.route_scores[route_length] = route_scores[route_length]

    def add_city(self, city_name, x=None, y=None):
        if city_name not in self.cities:
            self.cities.append(city_name)

        if x is not None and y is not None:
            self.city_positions[city_name] = {
                "x": x,
                "y": y
            }

    def add_route(
        self,
        city_a,
        city_b,
        colour,
        length,
        points=None,
        segment_points=None,
        route_type=RouteType.STANDARD,
        required_locomotives=0
    ):
        route_data = {
            "start": city_a,
            "end": city_b,
            "color": colour,
            "length": length,
            "route_type": route_type,
            "required_locomotives": required_locomotives
        }

        if points is not None:
            route_data["points"] = points

        if segment_points is not None:
            route_data["segment_points"] = segment_points

        self.routes.append(route_data)

    def add_ticket(self, city_a, city_b, points):
        self.tickets.append({
            "start": city_a,
            "end": city_b,
            "points": points
        })
