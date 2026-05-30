"""Controller layer for the game."""

from models.scoring import StandardScoring


class GameController:
    def __init__(self, turn_manager=None, scoring=None):
        self.turn_manager = turn_manager

        if scoring is None:
            self.scoring = StandardScoring()
        else:
            self.scoring = scoring

    def set_turn_manager(self, turn_manager):
        self.turn_manager = turn_manager

    def get_routes(self):
        # routes shown
        if self.turn_manager is None:
            return []

        return self.turn_manager.board.routes

    def map_name(self):
        if self.turn_manager is None:
            return "Unknown Map"

        return self.turn_manager.board.map_name

    def players(self):
        if self.turn_manager is None:
            return []

        return self.turn_manager.players

    def claim_route(self, route_index):
        # ui sends the selected route
        if self.turn_manager is None:
            return False, "Game has not been set up."

        routes = self.get_routes()

        if route_index is None or route_index < 0 or route_index >= len(routes):
            return False, "Select a valid route first."

        route = routes[route_index]
        return self.turn_manager.claim_route(route)

    def end_turn(self):
        if self.turn_manager is None:
            return "Game has not been set up."

        return self.turn_manager.next_turn()

    def current_player(self):
        if self.turn_manager is None:
            return None

        return self.turn_manager.get_current_player()

    def starting_ticket_choices(self):
        choices = []

        if self.turn_manager is None:
            return choices

        for player in self.turn_manager.players:
            if player.starting_ticket_choices:
                choices.append((player, player.starting_ticket_choices))

        return choices

    def choose_starting_tickets(self, player, kept_tickets, returned_tickets):
        if self.turn_manager is None:
            return False, "Game has not been set up."

        return self.turn_manager.choose_starting_tickets(
            player,
            kept_tickets,
            returned_tickets
        )

    def game_over(self):
        # stop actions after the game ends
        if self.turn_manager is None:
            return False

        return self.turn_manager.is_game_over()

    def final_scores(self):
        # scores shown once game is over
        if self.turn_manager is None:
            return {}

        players = self.turn_manager.players
        board = self.turn_manager.board
        return self.scoring.final_scores(players, board)

    def winners(self):
        # winner text shown by the ui
        if self.turn_manager is None:
            return []

        players = self.turn_manager.players
        board = self.turn_manager.board
        return self.scoring.winners(players, board)
    
    def draw_train_card(self, from_deck = False, pool_index = None):
        if self.turn_manager is None:
            return False, "Game has not been set up."

        if pool_index is not None:
            if pool_index < 0 or pool_index >= len(self.turn_manager.face_up_pool.face_up_cards):
                return False, "Select a valid face up card first."

        return self.turn_manager.draw_train_card(from_deck, pool_index)
    
    def draw_destination_tickets(self):
        if self.turn_manager is None:
            return False, "Game has not been set up."

        return self.turn_manager.draw_destination_tickets()

    def get_visible_destination_tickets(self):
        if self.turn_manager is None:
            return []

        return self.turn_manager.ticket_market.visible()

    def keep_destination_tickets(self, kept_tickets, returned_tickets):
        if self.turn_manager is None:
            return False, "Game has not been set up."

        return self.turn_manager.keep_destination_tickets(kept_tickets, returned_tickets)

    def get_face_up_cards(self):
        if self.turn_manager is None:
            return []
        return self.turn_manager.face_up_pool.face_up_cards

    def turn_ended(self):
        if self.turn_manager is None:
            return False
        return self.turn_manager.turn_ended()

