"""Destination ticket class."""


class DestinationTicket:
    def __init__(self, from_city, to_city, points):
        self.from_city = from_city
        self.to_city = to_city
        self.points = points

    def value(self):
        return self.points

    def is_complete(self, board, player):
        start_city = self.city_name(self.from_city)
        target_city = self.city_name(self.to_city)
        connected_cities = [start_city]
        changed = True

        # follow claimed routes until no more cities can be reached
        while changed:
            changed = False
            claimed_routes = board.claimed_routes(player)

            for route in claimed_routes:
                city_a = self.city_name(route.city_a)
                city_b = self.city_name(route.city_b)

                if city_a in connected_cities and city_b not in connected_cities:
                    connected_cities.append(city_b)
                    changed = True

                if city_b in connected_cities and city_a not in connected_cities:
                    connected_cities.append(city_a)
                    changed = True

        if target_city in connected_cities:
            return True

        return False

    def city_name(self, city):
        return getattr(city, "name", city)
