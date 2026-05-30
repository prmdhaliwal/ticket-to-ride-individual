"""Coloured transportation card class."""

from models.card_color import CardColor
from models.train_car_card import TrainCarCard


class ColouredCarCard(TrainCarCard):
    def matches(self, route_colour):
        if self.colour == route_colour or route_colour == CardColor.GRAY:
            return True

        return False
