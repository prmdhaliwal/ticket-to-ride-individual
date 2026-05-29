"""Route claim strategy interface."""


class RouteClaimStrategy:
    def can_claim(self, player, route):
        raise NotImplementedError
