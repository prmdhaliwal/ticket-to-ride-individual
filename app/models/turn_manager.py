"""Turn manager class."""

from models.card_color import CardColor
from models.destination_ticket_market import DestinationTicketMarket
from models.end_game_tracker import EndGameTracker
from models.route_claim_manager import RouteClaimManager
from models.subject import Subject


class TurnManager(Subject):
    """Manages the active player and validates actions."""
    def __init__(
        self,
        players,
        board,
        transport_deck,
        ticket_deck,
        face_up_pool,
        route_claim_manager=None,
        ticket_market=None
    ):
        super().__init__()
        self.players = players
        self.board = board
        self.transport_deck = transport_deck
        self.ticket_deck = ticket_deck
        self.face_up_pool = face_up_pool
        self.current_player_index = 0
        self.actions_taken = []
        self.end_game_tracker = EndGameTracker()

        if route_claim_manager is None:
            self.route_claim_manager = RouteClaimManager()
        else:
            self.route_claim_manager = route_claim_manager

        if ticket_market is None:
            self.ticket_market = DestinationTicketMarket()
        else:
            self.ticket_market = ticket_market

    def get_current_player(self):
        return self.players[self.current_player_index]

    def starting_tickets_chosen(self):
        for player in self.players:
            if player.starting_ticket_choices:
                return False

        return True

    def choose_starting_tickets(self, player, kept_tickets, returned_tickets):
        choices = player.starting_ticket_choices

        if not choices:
            return False, "No starting tickets to choose."

        if len(kept_tickets) < 1:
            return False, "You must keep at least one ticket."

        selected_tickets = kept_tickets + returned_tickets

        if len(selected_tickets) != len(choices):
            return False, "Choose what to do with each starting ticket."

        for ticket in selected_tickets:
            if ticket not in choices:
                return False, "Invalid starting ticket selection."

        player.take_tickets(kept_tickets)
        self.ticket_deck.return_tickets(returned_tickets)
        player.starting_ticket_choices = []
        self.notify()
        return True, "Starting tickets chosen."

    def claim_route(self, route):
        if self.end_game_tracker.game_over():
            return False, "The game is over."

        if not self.starting_tickets_chosen():
            return False, "Starting tickets must be chosen first."

        player = self.get_current_player()

        if self.actions_taken:
            return False, "Turn over or another action taken."

        ok, message = self.route_claim_manager.claim_route(
            player,
            route,
            self.board,
            self.transport_deck,
            len(self.players)
        )

        if not ok:
            return False, message

        self.actions_taken.append(("route_claimed", route))
        self.notify()  # Notify observers that the board state changed
        return True, message

    def next_turn(self):
        if self.end_game_tracker.game_over():
            return "The game is over."

        if not self.starting_tickets_chosen():
            return "Starting tickets must be chosen first."

        if not self.turn_ended():
            return "You must complete an action before you end your turn."

        player = self.get_current_player()

        # check final round when players end their turn
        final_round_started = self.end_game_tracker.check_final_round(player, len(self.players))

        if self.end_game_tracker.final_round and not final_round_started:
            self.end_game_tracker.use_final_turn()

        if self.end_game_tracker.game_over():
            self.notify()  # Notify observers of game end
            return "Game over."

        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.current_player_index = 0

        self.actions_taken = []
        self.notify()  # Notify observers that turn has changed
        return "Next turn."

    def is_game_over(self):
        return self.end_game_tracker.game_over()

    def turn_ended(self):
        """Checks if the current player's turn has ended."""
        # Check if no actions have been taken yet.
        if not self.actions_taken:
            return False

        # Get the first item of the last action taken.
        last_action = self.actions_taken[-1][0]

        # Turn ends immediately if a route is claimed.
        if last_action == "route_claimed":
            return True

        # Turn ends after keeping drawn destination tickets.
        if last_action == "destination_tickets_kept":
            return True

        # Turn ends if player has drawn two train cards or one face-up locomotive.
        if last_action == "train_card_drawn":
            drawn_cards = []

            for action in self.actions_taken:
                if action[0] == "train_card_drawn":
                    drawn_cards.append(action)

            if len(drawn_cards) >= 2:
                return True

            if len(drawn_cards) == 1:
                card = drawn_cards[0][1]
                source = drawn_cards[0][2]
                if card.colour == CardColor.LOCOMOTIVE and source == "face_up":
                    return True

        return False

    def draw_train_card(self, from_deck=False, pool_index=None):
        """Draws a single train car card from either the deck or face-up pool."""
        # Stop action if the game is already over.
        if self.end_game_tracker.game_over():
            return False, "The game is over."

        if not self.starting_tickets_chosen():
            return False, "Starting tickets must be chosen first."

        # Check if the player has taken actions that end their turn or prevent drawing cards.
        if self.actions_taken:
            if self.actions_taken[0][0] != "train_card_drawn":
                return False, "You have already taken a different action this turn."

            drawn_cards = []

            for action in self.actions_taken:
                if action[0] == "train_card_drawn":
                    drawn_cards.append(action)

            if len(drawn_cards) >= 2:
                return False, "Turn over."

            if len(drawn_cards) == 1:
                card = drawn_cards[0][1]
                source = drawn_cards[0][2]
                if card.colour == CardColor.LOCOMOTIVE and source == "face_up":
                    return False, "Turn over."

        current_player = self.get_current_player()

        if from_deck:
            # Blind draw from the transport deck.
            deck_card = self.transport_deck.draw_blind()
            if not deck_card:
                return False, "Deck is empty."
            current_player.take_train_card(deck_card)
            self.actions_taken.append(("train_card_drawn", deck_card, "blind"))
            self.notify()
            return True, "Blind card drawn."
        else:
            # Draw a specific card from the face-up pool.
            if pool_index is None or pool_index < 0 or pool_index >= len(self.face_up_pool.face_up_cards):
                return False, "Invalid face-up card index."

            pool_card = self.face_up_pool.face_up_cards[pool_index]

            # Prevent drawing a face-up locomotive as the second card.
            if pool_card.colour == CardColor.LOCOMOTIVE:
                if len(self.actions_taken) == 1:
                    return False, "Cannot draw a face-up Locomotive as your second card."

            # Remove from pool and refresh it.
            self.face_up_pool.draw_face_up(pool_index)
            self.face_up_pool.refresh(self.transport_deck)

            current_player.take_train_card(pool_card)
            self.actions_taken.append(("train_card_drawn", pool_card, "face_up"))
            self.notify()
            return True, "Face-up card drawn."

    def draw_destination_tickets(self):
        """Draws visible destination tickets for the player to choose from."""
        # Stop action if the game is already over.
        if self.end_game_tracker.game_over():
            return False, "The game is over."

        if not self.starting_tickets_chosen():
            return False, "Starting tickets must be chosen first."

        # Enforce that drawing tickets must be the first action.
        if self.actions_taken:
            return False, "Turn over or another action taken."

        # Fill the market if it has no visible tickets.
        if not self.ticket_market.visible():
            self.ticket_market.refill(self.ticket_deck)

        tickets = self.ticket_market.visible()
        if not tickets:
            return False, "No tickets left."

        self.actions_taken.append(("destination_tickets_drawn", tickets))
        self.notify()
        return tickets, "Destination cards drawn."

    def keep_destination_tickets(self, kept_tickets, returned_tickets):
        """Keeps selected destination tickets and returns the rest to the deck."""
        # Stop action if the game is already over.
        if self.end_game_tracker.game_over():
            return False, "The game is over."

        # Ensure tickets were drawn prior to keeping them.
        if not self.actions_taken or self.actions_taken[-1][0] != "destination_tickets_drawn":
            return False, "You must draw tickets first."

        current_player = self.get_current_player()
        ok, message = self.ticket_market.choose_tickets(
            current_player,
            kept_tickets,
            returned_tickets,
            self.ticket_deck
        )

        if not ok:
            return False, message

        self.actions_taken.append(("destination_tickets_kept", kept_tickets))
        self.notify()
        return True, message
