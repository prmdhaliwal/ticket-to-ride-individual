"""Configuration data for specific board layouts."""

import json
import os
import sys

from models.core import CardColor
from models.core import RouteType


class MapDefinition:
    def __init__(self, map_name, min_players, max_players, initial_train_pieces):
        self.map_name = map_name
        self.min_players = min_players
        self.max_players = max_players
        self.initial_train_pieces = initial_train_pieces
        
        self.cities = []
        self.city_positions = {}
        self.routes = []
        self.tickets = []
        self.layout_size = None
        
        # Scoring table specific to the London map
        self.route_scores = {
            1: 1, 
            2: 2, 
            3: 4, 
            4: 7
        }

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

    @classmethod
    def create_london_map(cls):
        # Initializing London with 17 initial train pieces per UML/London rules
        london = cls("London", 2, 4, 17)

        layout_loaded = london.load_layout_config(cls.london_layout_path())

        if not layout_loaded:
            # fallback data keeps the game runnable if the visual config is missing
            cities = [
                "Hyde Park", "Covent Garden", "Tower of London", "Waterloo", "Big Ben",
                "Baker Street", "Regent's Park", "Brick Lane", "King's Cross",
                "Elephant & Castle", "Piccadilly Circus", "St. Paul's", "British Museum",
                "Trafalgar Square", "Buckingham Palace", "The Charterhouse", "Globe Theatre"
            ]
            for city in cities:
                london.add_city(city)

            london.add_route("Hyde Park", "Covent Garden", CardColor.BLACK, 2)
            london.add_route("Covent Garden", "Tower of London", CardColor.PINK, 3)
            london.add_route("Covent Garden", "Waterloo", CardColor.YELLOW, 1)
            london.add_route("Buckingham Palace", "Big Ben", CardColor.GRAY, 1)
            london.add_route("Big Ben", "Trafalgar Square", CardColor.BLUE, 1)
            london.add_route("Trafalgar Square", "Piccadilly Circus", CardColor.GREEN, 1)
            london.add_route("Covent Garden", "British Museum", CardColor.ORANGE, 1)
        
        # London Destination Ticket deck
        tickets_data = [
            ("British Museum", "Piccadilly Circus", 2),
            ("Piccadilly Circus", "Waterloo", 3),
            ("Hyde Park", "Covent Garden", 3),
            ("Trafalgar Square", "Globe Theatre", 4),
            ("British Museum", "St. Paul's", 4),
            ("British Museum", "Waterloo", 4),
            ("Trafalgar Square", "St. Paul's", 4),
            ("Brick Lane", "Globe Theatre", 4),
            ("The Charterhouse", "Big Ben", 5),
            ("Baker Street", "Trafalgar Square", 5),
            ("Buckingham Palace", "Elephant & Castle", 5),
            ("Regent's Park", "Piccadilly Circus", 5),
            ("King's Cross", "Buckingham Palace", 6),
            ("Hyde Park", "St. Paul's", 6),
            ("Big Ben", "Tower of London", 6),
            ("King's Cross", "Tower of London", 7),
            ("Trafalgar Square", "Tower of London", 7),
            ("Buckingham Palace", "Brick Lane", 9),
            ("Regent's Park", "Elephant & Castle", 9),
            ("Baker Street", "Tower of London", 11)
        ]
        for city_a, city_b, points in tickets_data:
            london.add_city(city_a)
            london.add_city(city_b)
            london.add_ticket(city_a, city_b, points)
        
        return london

    @classmethod
    def london_layout_path(cls):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_path, "assets", "maps", "london_map_config.json")

    def load_layout_config(self, file_path):
        if not os.path.exists(file_path):
            return False

        with open(file_path, "r", encoding="utf-8") as config_file:
            data = json.load(config_file)

        self.layout_size = data.get("map_size")
        city_names_by_id = {}

        for city_data in data.get("cities", []):
            city_id = city_data.get("id")
            display_name = self.clean_city_name(city_data.get("display_name"))
            position = city_data.get("position", {})

            if city_id:
                city_names_by_id[city_id] = display_name

            self.add_city(display_name, position.get("x"), position.get("y"))

        for route_data in data.get("routes", []):
            from_id = route_data.get("from_city_id")
            to_id = route_data.get("to_city_id")
            city_a = city_names_by_id.get(from_id)
            city_b = city_names_by_id.get(to_id)

            if city_a is None or city_b is None:
                continue

            colour = self.colour_from_config(route_data.get("cart_type"))
            length = route_data.get("route_length", 1)
            points = self.points_from_config(route_data.get("points", []))
            segment_points = self.segment_points_from_config(route_data.get("segment_points", []))
            route_type = self.route_type_from_config(route_data.get("route_type"))
            required_locomotives = route_data.get("required_locomotives", 0)

            self.add_route(
                city_a,
                city_b,
                colour,
                length,
                points,
                segment_points,
                route_type,
                required_locomotives
            )

        return True

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
