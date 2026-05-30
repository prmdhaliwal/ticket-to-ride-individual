"""Scoring strategy interface."""


class ScoringStrategy:
    def final_scores(self, players, board):
        raise NotImplementedError

    def winners(self, players, board):
        raise NotImplementedError
