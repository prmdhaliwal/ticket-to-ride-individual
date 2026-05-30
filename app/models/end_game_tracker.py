"""Final round tracking class."""


class EndGameTracker:
    """Tracks the final round trigger (when a player hits 2 or fewer buses)."""
    def __init__(self):
        self.final_round = False
        self.triggering_player = None
        self.final_turns_remaining = 0
        self.game_finished = False

    def check_final_round(self, player, player_count):
        if self.final_round:
            return False

        if player.trains_left <= 2:
            self.final_round = True
            self.triggering_player = player
            self.final_turns_remaining = player_count
            return True

        return False

    def use_final_turn(self):
        if self.final_round and self.final_turns_remaining > 0:
            self.final_turns_remaining -= 1

        if self.final_round and self.final_turns_remaining == 0:
            self.game_finished = True

    def game_over(self):
        return self.game_finished
