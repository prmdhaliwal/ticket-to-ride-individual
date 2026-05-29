"""Game setup classes."""

from models.board import BoardMap
from models.player import Player
from models.decks import TrainCarCardDeck, DestinationTicketDeck, FaceUpPool
from models.cards import ColouredCarCard, LocomotiveCard
from models.tickets import DestinationTicket
from models.core import CardColor
from models.turns import TurnManager


class GameSetup:
    """Responsible for bootstrapping the game state from a MapDefinition."""
    
    def set_up_game(self, map_def, player_names):
        self.validate_player_count(map_def, player_names)

        board = self.create_board(map_def)
        players = self.create_players(player_names, map_def)
        
        # Build Decks
        transport_deck = self.create_train_deck()
        ticket_deck = self.create_ticket_deck(map_def)
        
        self.deal_starting_cards(players, transport_deck)
        self.deal_starting_tickets(players, ticket_deck)
        
        # Initialize the 5 face-up cards
        face_up_pool = FaceUpPool()
        face_up_pool.refresh(transport_deck)
        
        return TurnManager(players, board, transport_deck, ticket_deck, face_up_pool)

    def validate_player_count(self, map_def, player_names):
        player_count = len(player_names)

        if player_count < map_def.min_players or player_count > map_def.max_players:
            message = (
                f"{map_def.map_name} requires "
                f"{map_def.min_players}-{map_def.max_players} players."
            )
            raise ValueError(message)

    def create_players(self, names, map_def):
        players = []

        for name in names:
            player = Player(name, trains_left=map_def.initial_train_pieces)
            players.append(player)

        return players

    def create_board(self, map_def):
        return BoardMap(map_def)

    def deal_starting_cards(self, players, deck):
        for player in players:
            for _ in range(2):
                card = deck.draw_blind()
                if card:
                    player.take_train_card(card)

    def deal_starting_tickets(self, players, deck):
        for player in players:
            dealt = deck.draw_two()
            player.starting_ticket_choices = dealt

    def create_train_deck(self):
        """Creates the 44 cards for the London edition."""
        cards = []
        colors = [
            CardColor.BLUE,
            CardColor.GREEN,
            CardColor.BLACK,
            CardColor.PINK,
            CardColor.YELLOW,
            CardColor.ORANGE
        ]

        for color in colors:
            for _ in range(6):
                cards.append(ColouredCarCard(color))

        for _ in range(8):
            cards.append(LocomotiveCard())

        return TrainCarCardDeck(cards)

    def create_ticket_deck(self, map_def):
        """Creates the tickets based on the map definition."""
        tickets = []
        for t_data in map_def.tickets:
            tickets.append(DestinationTicket(t_data["start"], t_data["end"], t_data["points"]))
        return DestinationTicketDeck(tickets)
