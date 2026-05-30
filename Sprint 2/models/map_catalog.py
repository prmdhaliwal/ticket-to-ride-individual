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

        map_definition = MapDefinition(
            map_name,
            min_players,
            max_players,
            initial_train_pieces
        )
        map_definition.layout_size = config_data.get("map_size")
        map_definition.route_scores = self.route_scores_from_config(
            config_data.get("route_scores", {})
        )

        city_names_by_id = self.load_cities(map_definition, config_data)
        self.load_routes(map_definition, config_data, city_names_by_id)
        self.load_tickets(map_definition, config_data, city_names_by_id)

        return map_definition
    
    def route_scores_from_config(self, route_scores_data):
        route_scores = {}

        for route_length in route_scores_data:
            route_scores[int(route_length)] = route_scores_data[route_length]

        return route_scores 

    