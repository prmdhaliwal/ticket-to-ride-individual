import sys
import unittest
from collections import Counter
from pathlib import Path
"""
AI was used explicity to generate content in these tests but tests were thought of independently for london functionality
"""
SPRINT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SPRINT_DIR))

from controllers.game_controller import GameController
from controllers.game_setup import GameSetup
from models.board import BoardMap
from models.cards import ColouredCarCard, LocomotiveCard
from models.core import CardColor, RouteType
from models.decks import DestinationTicketDeck, FaceUpPool, TrainCarCardDeck
from models.destination_ticket_market import DestinationTicketMarket
from models.map_definition import MapDefinition
from models.player import Player
from models.scoring import StandardScoring
from models.tickets import DestinationTicket
from models.turns import TurnManager


class LondonRulesTest(unittest.TestCase):
    def make_small_map(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)

        for city in ["A", "B", "C", "D"]:
            map_definition.add_city(city)

        map_definition.add_ticket("A", "B", 1)
        map_definition.add_ticket("B", "C", 2)
        map_definition.add_ticket("C", "D", 3)
        map_definition.add_ticket("D", "A", 4)

        return map_definition

    def test_transport_deck_uses_london_card_counts(self):
        deck = GameSetup().create_train_deck()
        cards = deck.deck + deck.discard
        counts = Counter()

        for card in cards:
            counts[card.colour] += 1

        self.assertEqual(44, len(cards))
        self.assertEqual(8, counts[CardColor.LOCOMOTIVE])
        self.assertEqual(6, counts[CardColor.BLUE])
        self.assertEqual(6, counts[CardColor.GREEN])
        self.assertEqual(6, counts[CardColor.BLACK])
        self.assertEqual(6, counts[CardColor.PINK])
        self.assertEqual(6, counts[CardColor.YELLOW])
        self.assertEqual(6, counts[CardColor.ORANGE])
        self.assertEqual(0, counts[CardColor.RED])
        self.assertEqual(0, counts[CardColor.WHITE])

    def test_setup_deals_two_transport_cards_and_two_starting_ticket_choices(self):
        turn_manager = GameSetup().set_up_game(
            self.make_small_map(),
            ["Alice", "Bob"]
        )

        for player in turn_manager.players:
            self.assertEqual(2, len(player.train_cards))
            self.assertEqual(0, len(player.destination_tickets))
            self.assertEqual(2, len(player.starting_ticket_choices))

    def test_setup_creates_visible_ticket_market_after_starting_tickets(self):
        turn_manager = GameSetup().set_up_game(
            MapDefinition.create_london_map(),
            ["Alice", "Bob"]
        )

        self.assertEqual(3, len(turn_manager.ticket_market.visible()))

    def test_backend_setup_rejects_invalid_player_counts(self):
        map_definition = self.make_small_map()

        with self.assertRaises(ValueError):
            GameSetup().set_up_game(map_definition, ["Alice"])

        with self.assertRaises(ValueError):
            GameSetup().set_up_game(
                map_definition,
                ["Alice", "Bob", "Cara", "Dan", "Eli"]
            )

    def test_starting_ticket_choice_keeps_one_and_returns_one(self):
        turn_manager = GameSetup().set_up_game(
            self.make_small_map(),
            ["Alice", "Bob"]
        )

        ticket_deck = turn_manager.ticket_deck
        player = turn_manager.players[0]
        choices = player.starting_ticket_choices
        starting_deck_count = len(ticket_deck.tickets)

        ok, message = turn_manager.choose_starting_tickets(
            player,
            [choices[0]],
            [choices[1]]
        )

        self.assertTrue(ok)
        self.assertEqual(1, len(player.destination_tickets))
        self.assertEqual(0, len(player.starting_ticket_choices))
        self.assertIn(choices[1], ticket_deck.tickets)
        self.assertEqual(starting_deck_count + 1, len(ticket_deck.tickets))

    def test_london_map_uses_london_settings_and_route_scores(self):
        london = MapDefinition.create_london_map()
        actual_scores = {}

        for route_length in london.route_scores:
            actual_scores[route_length] = london.route_scores[route_length]

        expected_scores = {
            1: 1,
            2: 2,
            3: 4,
            4: 7
        }

        self.assertEqual("London", london.map_name)
        self.assertEqual(2, london.min_players)
        self.assertEqual(4, london.max_players)
        self.assertEqual(17, london.initial_train_pieces)
        self.assertEqual(expected_scores, actual_scores)
        self.assertEqual(17, len(london.cities))
        self.assertEqual(43, len(london.routes))
        self.assertEqual({"x": 953.0, "y": 612.0}, london.layout_size)

    def test_london_destination_tickets_use_london_locations(self):
        london = MapDefinition.create_london_map()
        actual_tickets = []

        for ticket in london.tickets:
            actual_tickets.append((
                ticket["start"],
                ticket["end"],
                ticket["points"]
            ))

        expected_tickets = [
            ("British Museum", "Piccadilly Circus", 2),
            ("Piccadilly Circus", "Waterloo", 3),
            ("Hyde Park", "Covent Garden", 3),
            ("Trafalgar Square", "Globe Theatre", 4),
            ("British Museum", "St. Paul's", 4),
            ("British Museum", "Waterloo", 4),
            ("Trafalgar Square", "St. Paul's", 4),
            ("Brick Lane", "Globe Theatre", 4),
            ("The Charterhouse", "Big Ben", 5),
            ("Baker Street", "Trafalgar Square", 5),
            ("Buckingham Palace", "Elephant & Castle", 5),
            ("Regent's Park", "Piccadilly Circus", 5),
            ("King's Cross", "Buckingham Palace", 6),
            ("Hyde Park", "St. Paul's", 6),
            ("Big Ben", "Tower of London", 6),
            ("King's Cross", "Tower of London", 7),
            ("Trafalgar Square", "Tower of London", 7),
            ("Buckingham Palace", "Brick Lane", 9),
            ("Regent's Park", "Elephant & Castle", 9),
            ("Baker Street", "Tower of London", 11)
        ]

        self.assertEqual(20, len(actual_tickets))
        self.assertEqual(set(expected_tickets), set(actual_tickets))
        self.assertNotIn(("Trafalgar Square", "Camden", 4), actual_tickets)
        self.assertNotIn(("Marylebone", "Borough Market", 4), actual_tickets)

    def test_london_map_uses_pink_not_purple_routes(self):
        london = MapDefinition.create_london_map()
        route_colours = []

        for route in london.routes:
            route_colours.append(route["color"])

        self.assertIn(CardColor.PINK, route_colours)
        self.assertNotIn(CardColor.PURPLE, route_colours)

    def test_london_map_contains_ferry_route(self):
        london = MapDefinition.create_london_map()
        ferry_routes = []

        for route in london.routes:
            if route["route_type"] == RouteType.FERRY:
                ferry_routes.append(route)

        self.assertGreaterEqual(len(ferry_routes), 1)
        self.assertEqual("Tower of London", ferry_routes[0]["start"])
        self.assertEqual("Globe Theatre", ferry_routes[0]["end"])
        self.assertEqual(CardColor.GRAY, ferry_routes[0]["color"])
        self.assertEqual(3, ferry_routes[0]["length"])
        self.assertEqual(RouteType.FERRY, ferry_routes[0]["route_type"])
        self.assertEqual(1, ferry_routes[0]["required_locomotives"])
        self.assertEqual(5, len(ferry_routes[0]["points"]))
        self.assertEqual(3, len(ferry_routes[0]["segment_points"]))

    def test_routes_default_to_standard_route_type(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        route_data = map_definition.routes[0]
        route = board.routes[0]

        self.assertEqual(RouteType.STANDARD, route_data["route_type"])
        self.assertEqual(0, route_data["required_locomotives"])
        self.assertEqual(RouteType.STANDARD, route.route_type)
        self.assertEqual(0, route.required_locomotives)

    def test_routes_keep_ferry_route_details(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route(
            "A",
            "B",
            CardColor.GRAY,
            3,
            route_type=RouteType.FERRY,
            required_locomotives=1
        )

        board = BoardMap(map_definition)
        route_data = map_definition.routes[0]
        route = board.routes[0]

        self.assertEqual(RouteType.FERRY, route_data["route_type"])
        self.assertEqual(1, route_data["required_locomotives"])
        self.assertEqual(RouteType.FERRY, route.route_type)
        self.assertEqual(1, route.required_locomotives)

    def test_claim_route_places_buses_and_discards_cards(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        player.take_train_card(ColouredCarCard(CardColor.BLUE))
        player.take_train_card(ColouredCarCard(CardColor.BLUE))

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertTrue(ok)
        self.assertEqual("Route claimed.", message)
        self.assertEqual(player, route.owner)
        self.assertEqual(15, player.trains_left)
        self.assertEqual(2, player.score)
        self.assertEqual(0, len(player.train_cards))
        self.assertEqual(2, len(transport_deck.discard))
        self.assertEqual(2, len(route.placed_trains))
        self.assertTrue(turn_manager.turn_ended())

    def test_claim_route_rejects_route_not_on_board(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        other_map_definition = MapDefinition("Other London", 2, 4, 17)
        other_map_definition.add_city("C")
        other_map_definition.add_city("D")
        other_map_definition.add_route("C", "D", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        other_board = BoardMap(other_map_definition)
        player = Player("Alice")
        other_player = Player("Bob")

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = other_board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertFalse(ok)
        self.assertEqual("That route is not on the board.", message)
        self.assertIsNone(route.owner)

    def test_claim_route_rejects_already_claimed_route(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        route = board.routes[0]
        route.claim(other_player)

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )

        ok, message = turn_manager.claim_route(route)

        self.assertFalse(ok)
        self.assertEqual("That route has already been claimed.", message)
        self.assertEqual(other_player, route.owner)

    def test_claim_route_rejects_without_enough_bus_pieces(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        player = Player("Alice", trains_left=1)
        other_player = Player("Bob")

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertFalse(ok)
        self.assertEqual("Not enough bus pieces.", message)
        self.assertIsNone(route.owner)
        self.assertEqual(1, player.trains_left)

    def test_claim_route_rejects_without_matching_cards(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route("A", "B", CardColor.BLUE, 2)

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        player.take_train_card(ColouredCarCard(CardColor.GREEN))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertFalse(ok)
        self.assertEqual("Not enough matching transportation cards.", message)
        self.assertIsNone(route.owner)
        self.assertEqual(17, player.trains_left)
        self.assertEqual(2, len(player.train_cards))
        self.assertEqual(0, len(transport_deck.discard))

    def test_claim_ferry_route_with_required_locomotive(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route(
            "A",
            "B",
            CardColor.BLUE,
            2,
            route_type=RouteType.FERRY,
            required_locomotives=1
        )

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        player.take_train_card(LocomotiveCard())
        player.take_train_card(ColouredCarCard(CardColor.BLUE))

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertTrue(ok)
        self.assertEqual("Route claimed.", message)
        self.assertEqual(player, route.owner)
        self.assertEqual(15, player.trains_left)
        self.assertEqual(2, player.score)
        self.assertEqual(0, len(player.train_cards))
        self.assertEqual(2, len(transport_deck.discard))
        self.assertEqual(2, len(route.placed_trains))

    def test_claim_ferry_route_with_three_extra_cards_for_missing_locomotive(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route(
            "A",
            "B",
            CardColor.BLUE,
            2,
            route_type=RouteType.FERRY,
            required_locomotives=1
        )

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        player.take_train_card(ColouredCarCard(CardColor.BLUE))
        player.take_train_card(ColouredCarCard(CardColor.BLUE))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertTrue(ok)
        self.assertEqual("Route claimed.", message)
        self.assertEqual(player, route.owner)
        self.assertEqual(15, player.trains_left)
        self.assertEqual(2, player.score)
        self.assertEqual(0, len(player.train_cards))
        self.assertEqual(5, len(transport_deck.discard))
        self.assertEqual(2, len(route.placed_trains))

    def test_claim_ferry_route_rejects_without_substitute_cards(self):
        map_definition = MapDefinition("Test London", 2, 4, 17)
        map_definition.add_city("A")
        map_definition.add_city("B")
        map_definition.add_route(
            "A",
            "B",
            CardColor.BLUE,
            2,
            route_type=RouteType.FERRY,
            required_locomotives=1
        )

        board = BoardMap(map_definition)
        player = Player("Alice")
        other_player = Player("Bob")
        player.take_train_card(ColouredCarCard(CardColor.BLUE))
        player.take_train_card(ColouredCarCard(CardColor.BLUE))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))
        player.take_train_card(ColouredCarCard(CardColor.GREEN))

        transport_deck = TrainCarCardDeck([])
        ticket_deck = DestinationTicketDeck([])
        face_up_pool = FaceUpPool()
        turn_manager = TurnManager(
            [player, other_player],
            board,
            transport_deck,
            ticket_deck,
            face_up_pool
        )
        route = board.routes[0]

        ok, message = turn_manager.claim_route(route)

        self.assertFalse(ok)
        self.assertEqual("Not enough matching transportation cards.", message)
        self.assertIsNone(route.owner)
        self.assertEqual(17, player.trains_left)
        self.assertEqual(4, len(player.train_cards))
        self.assertEqual(0, len(transport_deck.discard))

    def test_face_up_pool_discards_and_replaces_three_buses(self):
        pool = FaceUpPool()
        pool.face_up_cards = [
            LocomotiveCard(),
            LocomotiveCard(),
            LocomotiveCard(),
            ColouredCarCard(CardColor.BLUE),
            ColouredCarCard(CardColor.GREEN),
        ]

        deck = TrainCarCardDeck([])
        deck.deck = [
            ColouredCarCard(CardColor.BLACK),
            ColouredCarCard(CardColor.PINK),
            ColouredCarCard(CardColor.YELLOW),
            ColouredCarCard(CardColor.ORANGE),
            ColouredCarCard(CardColor.BLUE),
        ]

        pool.replace_if_three_buses(deck)

        bus_count = 0

        for card in pool.face_up_cards:
            if card.colour == CardColor.LOCOMOTIVE:
                bus_count += 1

        self.assertEqual(5, len(pool.face_up_cards))
        self.assertEqual(5, len(deck.discard))
        self.assertLess(bus_count, 3)

    def test_face_up_bus_as_first_transport_card_ends_turn(self):
        player = Player("Alice")
        pool = FaceUpPool()
        pool.face_up_cards = [
            LocomotiveCard(),
            ColouredCarCard(CardColor.BLUE),
            ColouredCarCard(CardColor.GREEN),
            ColouredCarCard(CardColor.BLACK),
            ColouredCarCard(CardColor.YELLOW),
        ]

        deck = TrainCarCardDeck([])
        deck.deck = [ColouredCarCard(CardColor.ORANGE)]

        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            deck,
            DestinationTicketDeck([]),
            pool
        )

        ok, message = turn_manager.draw_train_card(False, 0)

        self.assertTrue(ok)
        self.assertTrue(turn_manager.turn_ended())
        self.assertEqual(1, len(player.train_cards))
        self.assertEqual(CardColor.LOCOMOTIVE, player.train_cards[0].colour)
        self.assertEqual(5, len(pool.face_up_cards))

    def test_face_up_bus_cannot_be_second_transport_card(self):
        player = Player("Alice")
        pool = FaceUpPool()
        pool.face_up_cards = [
            LocomotiveCard(),
            ColouredCarCard(CardColor.BLUE),
            ColouredCarCard(CardColor.GREEN),
            ColouredCarCard(CardColor.BLACK),
            ColouredCarCard(CardColor.YELLOW),
        ]

        deck = TrainCarCardDeck([])
        deck.deck = [ColouredCarCard(CardColor.ORANGE)]

        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            deck,
            DestinationTicketDeck([]),
            pool
        )

        ok, message = turn_manager.draw_train_card(True)
        self.assertTrue(ok)

        ok, message = turn_manager.draw_train_card(False, 0)

        self.assertFalse(ok)
        self.assertEqual(1, len(player.train_cards))

    def test_draw_destination_tickets_shows_three_market_tickets_and_keeps_one(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
            DestinationTicket("D", "E", 4),
            DestinationTicket("E", "F", 5),
            DestinationTicket("F", "G", 6),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            TrainCarCardDeck([]),
            ticket_deck,
            FaceUpPool()
        )

        drawn, message = turn_manager.draw_destination_tickets()
        self.assertEqual("Destination cards drawn.", message)
        self.assertEqual(3, len(drawn))
        self.assertEqual(drawn, turn_manager.ticket_market.visible())

        returned_tickets = [drawn[1], drawn[2]]
        ok, message = turn_manager.keep_destination_tickets([drawn[0]], returned_tickets)

        self.assertTrue(ok)
        self.assertEqual("Tickets kept.", message)
        self.assertTrue(turn_manager.turn_ended())
        self.assertEqual(1, len(player.destination_tickets))
        self.assertEqual(drawn[0], player.destination_tickets[0])
        self.assertEqual(3, len(turn_manager.ticket_market.visible()))

        for ticket in returned_tickets:
            self.assertIn(ticket, ticket_deck.tickets)

    def test_draw_destination_tickets_rejects_after_action_taken(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            TrainCarCardDeck([]),
            ticket_deck,
            FaceUpPool()
        )
        turn_manager.actions_taken.append((
            "train_card_drawn",
            ColouredCarCard(CardColor.BLUE),
            "blind"
        ))

        ok, message = turn_manager.draw_destination_tickets()

        self.assertFalse(ok)
        self.assertEqual("Turn over or another action taken.", message)

    def test_ticket_market_fills_up_to_three_tickets(self):
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
            DestinationTicket("D", "E", 4),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        market = DestinationTicketMarket()

        market.refill(ticket_deck)

        self.assertEqual(3, len(market.visible()))
        self.assertEqual(1, len(ticket_deck.tickets))

    def test_ticket_market_can_show_fewer_than_three_tickets(self):
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        market = DestinationTicketMarket()

        market.refill(ticket_deck)

        self.assertEqual(2, len(market.visible()))
        self.assertEqual(0, len(ticket_deck.tickets))

    def test_ticket_market_keeps_selected_tickets(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
            DestinationTicket("D", "E", 4),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        market = DestinationTicketMarket()
        market.refill(ticket_deck)
        visible_tickets = market.visible()

        ok, message = market.choose_tickets(
            player,
            [visible_tickets[0]],
            [visible_tickets[1], visible_tickets[2]],
            ticket_deck
        )

        self.assertTrue(ok)
        self.assertEqual("Tickets kept.", message)
        self.assertEqual(1, len(player.destination_tickets))
        self.assertEqual(visible_tickets[0], player.destination_tickets[0])

    def test_ticket_market_returns_rejected_tickets(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
            DestinationTicket("D", "E", 4),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        market = DestinationTicketMarket()
        market.refill(ticket_deck)
        visible_tickets = market.visible()
        rejected_tickets = [visible_tickets[1], visible_tickets[2]]

        ok, message = market.choose_tickets(
            player,
            [visible_tickets[0]],
            rejected_tickets,
            ticket_deck
        )

        self.assertTrue(ok)

        for ticket in rejected_tickets:
            self.assertIn(ticket, ticket_deck.tickets)

    def test_ticket_market_rejects_choosing_zero_tickets(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        market = DestinationTicketMarket()
        market.refill(ticket_deck)
        visible_tickets = market.visible()

        ok, message = market.choose_tickets(
            player,
            [],
            visible_tickets,
            ticket_deck
        )

        self.assertFalse(ok)
        self.assertEqual("You must keep at least one ticket.", message)
        self.assertEqual(0, len(player.destination_tickets))
        self.assertEqual(3, len(market.visible()))

    def test_game_controller_draw_train_card_delegates_to_turn_manager(self):
        player = Player("Alice")
        pool = FaceUpPool()
        pool.face_up_cards = [
            ColouredCarCard(CardColor.BLUE),
            ColouredCarCard(CardColor.GREEN),
            ColouredCarCard(CardColor.BLACK),
            ColouredCarCard(CardColor.YELLOW),
            ColouredCarCard(CardColor.ORANGE),
        ]

        deck = TrainCarCardDeck([])
        deck.deck = [ColouredCarCard(CardColor.PINK)]

        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            deck,
            DestinationTicketDeck([]),
            pool
        )
        controller = GameController(turn_manager)

        ok, message = controller.draw_train_card(False, 0)

        self.assertTrue(ok)
        self.assertEqual(1, len(player.train_cards))

    def test_game_controller_returns_visible_destination_tickets(self):
        player = Player("Alice")
        tickets = [
            DestinationTicket("A", "B", 1),
            DestinationTicket("B", "C", 2),
            DestinationTicket("C", "D", 3),
        ]

        ticket_deck = DestinationTicketDeck(tickets)
        turn_manager = TurnManager(
            [player, Player("Bob")],
            object(),
            TrainCarCardDeck([]),
            ticket_deck,
            FaceUpPool()
        )
        controller = GameController(turn_manager)

        drawn, message = controller.draw_destination_tickets()
        visible_tickets = controller.get_visible_destination_tickets()

        self.assertEqual("Destination cards drawn.", message)
        self.assertEqual(drawn, visible_tickets)
        self.assertEqual(3, len(visible_tickets))


if __name__ == "__main__":
    unittest.main()
