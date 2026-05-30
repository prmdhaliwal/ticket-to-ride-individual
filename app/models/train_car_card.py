"""Transportation card base class."""


class TrainCarCard:
    def __init__(self, colour):
        self.colour = colour

    def matches(self, route_colour):
        return False
