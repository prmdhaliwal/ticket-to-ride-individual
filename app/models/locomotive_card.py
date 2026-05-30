"""Locomotive card class."""

from models.card_color import CardColor
from models.train_car_card import TrainCarCard


class LocomotiveCard(TrainCarCard):
    def __init__(self):
        super().__init__(CardColor.LOCOMOTIVE)

    def matches(self, route_colour):
        return True
