"""Standard route claiming rules."""

from models.route_claim_strategy import RouteClaimStrategy


class StandardRouteClaimStrategy(RouteClaimStrategy):
    def can_claim(self, player, route):
        if player.trains_left < route.length:
            return False, "Not enough bus pieces.", []

        cards_to_use = player.choose_cards_for_route(route)
        if len(cards_to_use) < route.length:
            return False, "Not enough matching transportation cards.", []

        return True, "Route claimed.", cards_to_use
