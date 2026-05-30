"""Standard final scoring rules."""

from models.scoring_strategy import ScoringStrategy


class StandardScoring(ScoringStrategy):
    LONGEST_PATH_BONUS = 10

    def final_scores(self, players, board):
        scores = {}
        longest_path_players = self.longest_path_players(players, board)

        for player in players:
            total = player.score

            for ticket in player.destination_tickets:
                if ticket.is_complete(board, player):
                    total += ticket.value()
                else:
                    total -= ticket.value()

            if player in longest_path_players:
                total += self.LONGEST_PATH_BONUS

            scores[player] = total

        return scores

    def winners(self, players, board):
        # start by finding players with the highest score
        scores = self.final_scores(players, board)
        winners = []
        best_score = None

        for player in players:
            player_score = scores[player]

            if best_score is None or player_score > best_score:
                best_score = player_score
                winners = []
                winners.append(player)
            elif player_score == best_score:
                winners.append(player)

        winners = self.tie_by_completed_tickets(winners, board)
        return winners

    def tie_by_completed_tickets(self, players, board):
        # first tie breaker is completed tickets
        tied = []
        best_count = None

        for player in players:
            completed = self.completed_ticket_count(player, board)

            if best_count is None or completed > best_count:
                best_count = completed
                tied = []
                tied.append(player)
            elif completed == best_count:
                tied.append(player)

        return tied

    def longest_path_players(self, players, board):
        winners = []
        best_length = 0

        for player in players:
            length = self.longest_path_length(player, board)

            if length > best_length:
                best_length = length
                winners = []
                winners.append(player)
            elif length == best_length and length > 0:
                winners.append(player)

        return winners

    def longest_path_length(self, player, board):
        claimed_routes = board.claimed_routes(player)
        cities = []
        best_length = 0

        for route in claimed_routes:
            if route.city_a not in cities:
                cities.append(route.city_a)

            if route.city_b not in cities:
                cities.append(route.city_b)

        for city in cities:
            length = self.longest_path_from_city(city, claimed_routes, [])

            if length > best_length:
                best_length = length

        return best_length

    def longest_path_from_city(self, city, routes, used_routes):
        best_length = 0

        for route in routes:
            if route in used_routes:
                continue

            next_city = None

            if route.city_a == city:
                next_city = route.city_b

            if route.city_b == city:
                next_city = route.city_a

            if next_city is not None:
                new_used_routes = used_routes.copy()
                new_used_routes.append(route)

                length = route.length + self.longest_path_from_city(
                    next_city,
                    routes,
                    new_used_routes
                )

                if length > best_length:
                    best_length = length

        return best_length

    def completed_ticket_count(self, player, board):
        # count tickets where both cities are connected
        completed = 0

        for ticket in player.destination_tickets:
            if ticket.is_complete(board, player):
                completed += 1

        return completed
