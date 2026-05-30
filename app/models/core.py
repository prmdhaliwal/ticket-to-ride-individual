"""Core enumerations and base patterns."""

from enum import Enum


class CardColor(Enum):
    RED = "Red"
    BLUE = "Blue"
    GREEN = "Green"
    YELLOW = "Yellow"
    BLACK = "Black"
    WHITE = "White"
    ORANGE = "Orange"
    PINK = "Pink"
    PURPLE = "Purple"
    GRAY = "Gray"
    LOCOMOTIVE = "Locomotive"


class RouteType(Enum):
    STANDARD = "Standard"
    FERRY = "Ferry"


class Observer:
    def update(self):
        pass


class Subject:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def detach(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update()
