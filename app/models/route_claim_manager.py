"""Route claiming coordination."""

from models.route_type import RouteType
from models.train_car import TrainCar
from models.ferry_route_claim_strategy import FerryRouteClaimStrategy
from models.standard_route_claim_strategy import StandardRouteClaimStrategy


class RouteClaimManager:
    def __init__(self, standard_strategy=None, ferry_strategy=None):
        if standard_strategy is None:
            self.standard_strategy = StandardRouteClaimStrategy()
        else:
            self.standard_strategy = standard_strategy

        if ferry_strategy is None:
            self.ferry_strategy = FerryRouteClaimStrategy()
        else:
            self.ferry_strategy = ferry_strategy

        self.strategies = {}
        self.strategies[RouteType.STANDARD] = self.standard_strategy
        self.strategies[RouteType.FERRY] = self.ferry_strategy

    def claim_route(self, player, route, board, transport_deck, player_count):
        if route not in board.routes:
            return False, "That route is not on the board."

        if not route.is_available(player_count, player):
            return False, "That route has already been claimed."

        strategy = self.strategy_for_route(route)
        ok, message, cards_to_use = strategy.can_claim(player, route)
        if not ok:
            return False, message

        player.remove_cards(cards_to_use)
        transport_deck.discard_cards(cards_to_use)
        player.place_trains(route.length)
        player.move_score(route.points(board.route_scores))

        route.claim(player)
        route.placed_trains = []

        # bus pieces now on the claimed route
        for _ in range(route.length):
            train = TrainCar(player, route)
            route.placed_trains.append(train)

        return True, "Route claimed."

    def strategy_for_route(self, route):
        route_type = getattr(route, "route_type", RouteType.STANDARD)

        if route_type in self.strategies:
            return self.strategies[route_type]

        return self.standard_strategy
