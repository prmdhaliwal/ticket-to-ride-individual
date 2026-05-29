"""Route claiming coordination."""

from models.cards import TrainCar
from models.standard_route_claim_strategy import StandardRouteClaimStrategy


class RouteClaimManager:
    def __init__(self, standard_strategy=None):
        if standard_strategy is None:
            self.standard_strategy = StandardRouteClaimStrategy()
        else:
            self.standard_strategy = standard_strategy

    def claim_route(self, player, route, board, transport_deck, player_count):
        if route not in board.routes:
            return False, "That route is not on the board."

        if not route.is_available(player_count, player):
            return False, "That route has already been claimed."

        ok, message, cards_to_use = self.standard_strategy.can_claim(player, route)
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
