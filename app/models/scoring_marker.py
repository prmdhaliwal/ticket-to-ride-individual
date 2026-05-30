"""Scoring marker class."""


class ScoringMarker:
    def __init__(self):
        self.position = 0

    def move_by(self, points):
        self.position += points
