"""Transportation card and bus piece classes."""

from models.core import CardColor


class TrainCarCard:
    def __init__(self, colour):
        self.colour = colour

    def matches(self, route_colour):
        return False


class ColouredCarCard(TrainCarCard):
    def matches(self, route_colour):
        if self.colour == route_colour or route_colour == CardColor.GRAY:
            return True

        return False


class LocomotiveCard(TrainCarCard):
    def __init__(self):
        super().__init__(CardColor.LOCOMOTIVE)

    def matches(self, route_colour):
        return True


class TrainCar:
    def __init__(self, owner=None, route=None):
        self.owner = owner
        self.route = route