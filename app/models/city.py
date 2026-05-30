"""City class."""


class City:
    def __init__(self, name, x=None, y=None):
        self.name = name
        self.x = x
        self.y = y

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if other is None:
            return False

        if self.name == other.name:
            return True

        return False

    def __hash__(self):
        return hash(self.name)
