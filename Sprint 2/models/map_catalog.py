"""Loads map definitions from JSON configuration files."""

import json
import os
import sys

from models.core import CardColor
from models.core import RouteType
from models.map_definition import MapDefinition


class MapCatalog:
    def __init__(self, map_folder=None):
        if map_folder is None:
            self.map_folder = self.default_map_folder()
        else:
            self.map_folder = map_folder

    def available_maps(self):
        map_names = []

        if not os.path.isdir(self.map_folder):
            return map_names

        for file_name in os.listdir(self.map_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.map_folder, file_name)
                config_data = self.read_config(file_path)
                map_name = config_data.get("map_name")

                if map_name is not None:
                    map_names.append(map_name)

        map_names.sort()
        return map_names

    def load_map(self, map_name):
        if not os.path.isdir(self.map_folder):
            raise ValueError(f"Map '{map_name}' was not found.")

        for file_name in os.listdir(self.map_folder):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.map_folder, file_name)
                config_data = self.read_config(file_path)

                if config_data.get("map_name") == map_name:
                    return self.build_map_definition(config_data)

        raise ValueError(f"Map '{map_name}' was not found.")

    def default_map_folder(self):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, "assets", "maps")

    def read_config(self, file_path):
        with open(file_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def build_map_definition(self, config_data):
        map_name = config_data.get("map_name", "Unknown Map")
        min_players = config_data.get("min_players", 2)
        max_players = config_data.get("max_players", 4)
        initial_train_pieces = config_data.get("initial_train_pieces", 17)
        route_scores = self.route_scores_from_config(
            config_data.get("route_scores", {})
        )

        map_definition = MapDefinition(
            map_name,
            min_players,
            max_players,
            initial_train_pieces,
            route_scores
        )
        map_definition.layout_size = config_data.get("map_size")

        city_names_by_id = self.load_cities(map_definition, config_data)
        self.load_routes(map_definition, config_data, city_names_by_id)
        self.load_tickets(map_definition, config_data, city_names_by_id)

        return map_definition
    
    def route_scores_from_config(self, route_scores_data):
        route_scores = {}

        for route_length in route_scores_data:
            route_scores[int(route_length)] = route_scores_data[route_length]

        return route_scores 

    def load_cities(self, map_definition, config_data):
        city_names_by_id = {}

        for city_data in config_data.get("cities", []):
            city_id = city_data.get("id")
            display_name = self.clean_city_name(city_data.get("display_name"))
            position = city_data.get("position", {})

            if city_id:
                city_names_by_id[city_id] = display_name

            map_definition.add_city(
                display_name,
                position.get("x"),
                position.get("y")
            )

        return city_names_by_id

    def load_routes(self, map_definition, config_data, city_names_by_id):
        for route_data in config_data.get("routes", []):
            from_id = route_data.get("from_city_id")
            to_id = route_data.get("to_city_id")
            city_a = city_names_by_id.get(from_id)
            city_b = city_names_by_id.get(to_id)

            if city_a is not None and city_b is not None:
                colour = self.colour_from_config(route_data.get("cart_type"))
                length = route_data.get("route_length", 1)
                points = self.points_from_config(route_data.get("points", []))
                segment_points = self.segment_points_from_config(
                    route_data.get("segment_points", [])
                )
                route_type = self.route_type_from_config(route_data.get("route_type"))
                required_locomotives = route_data.get("required_locomotives", 0)

                map_definition.add_route(
                    city_a,
                    city_b,
                    colour,
                    length,
                    points,
                    segment_points,
                    route_type,
                    required_locomotives
                )

    def clean_city_name(self, name):
        replacements = {
            "It Park": "Regent's Park",
            "Covent Gardens": "Covent Garden",
            "Kings Cross": "King's Cross",
            "ST Pauls": "St. Paul's",
            "TOL": "Tower of London",
            "Elephant": "Elephant & Castle"
        }

        if name in replacements:
            return replacements[name]

        return name

    def colour_from_config(self, colour_name):
        if colour_name is None:
            return CardColor.GRAY

        if colour_name == "NONE":
            return CardColor.GRAY

        upper_name = colour_name.upper()
        if upper_name == "PURPLE":
            return CardColor.PINK

        if upper_name in CardColor.__members__:
            return CardColor[upper_name]

        return CardColor.GRAY

    def route_type_from_config(self, route_type_name):
        if route_type_name is None:
            return RouteType.STANDARD

        upper_name = route_type_name.upper()

        if upper_name in RouteType.__members__:
            return RouteType[upper_name]

        return RouteType.STANDARD

    def points_from_config(self, points_data):
        points = []

        for point in points_data:
            points.append({
                "x": point.get("x"),
                "y": point.get("y")
            })

        return points

    def segment_points_from_config(self, segment_data):
        points = []

        for segment in segment_data:
            position = segment.get("position", {})
            points.append({
                "x": position.get("x"),
                "y": position.get("y"),
                "rotation": segment.get("rotation_radians")
            })

        return points
        
    def load_tickets(self, map_definition, config_data, city_names_by_id):
        for ticket_data in config_data.get("tickets", []):
            from_id = ticket_data.get("from_city_id")
            to_id = ticket_data.get("to_city_id")
            city_a = city_names_by_id.get(from_id)
            city_b = city_names_by_id.get(to_id)

            if city_a is not None and city_b is not None:
                map_definition.add_ticket(
                    city_a,
                    city_b,
                    ticket_data.get("points", 0)
                )

   
