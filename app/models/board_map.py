"""Board map class."""

from models.city import City
from models.route import Route
from models.route_type import RouteType


class BoardMap:
    def __init__(self, map_definition=None):
        self.map_name = "Unknown Map"
        self.cities = {}
        self.routes = []
        self.route_scores = {}
        self.layout_size = None

        if map_definition is not None:
            self.map_name = map_definition.map_name
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
