from sympy.utilities.iterables import multiset_permutations
import random
from numpy import pad
import copy


class Board:
    def __init__(self, players):
        self.winning_score = 41
        self.board_length = 11
        self.step_sizes = dict([(x, -3) if x == 11 else (x, x) for x in range(self.board_length)])

        self.players = players
        self.num_players = len(players)
        self.num_agents = min(self.num_players + 3, 7)

        self.state = self.start()

    def currentPlayer(self, state):
        return state.get("current_player")

    def display(self, state):
        print(state)

    def isEnded(self, state):
        return any([x > self.winning_score for x in state.get("agent_scores")])

    def isWinner(self, state):
        if max(state.get("agent_scores")) <= 41:
            return None
        else:
            winning_agents = [agent for agent, score in enumerate(state.get("agent_scores"))
                              if score == max(state.get("agent_scores"))]
            winning_players = []
            for i, player in enumerate(self.players):
                agent = state.get("player_agent_associations")[i]
                if agent in winning_agents:
                    winning_players.append(player)

        for i, player in enumerate(self.players):
            agent = state.get("player_agent_associations")[i]
            if state.get("agent_scores")[agent] > self.winning_score:
                return player

    def getState(self):
        return self.state

    def legalMoves(self, state):
        dice = self._rollDice()
        base = [x for x in list(self._compositions(dice)) if len(x) <= self.num_agents]
        padded = [pad(x, (0, max(0, self.num_agents - len(x))), "constant") for x in base]
        full = [list(multiset_permutations(x)) for x in padded]
        moves = [item for sublist in full for item in sublist]

        for i, move in enumerate(list(moves)):  # list hier notwendig, sonst wird über Original iteriert, während pop()
            if self._hypotheticalValidation(state, move):
                for x in self._hypotheticalNewTresorPositions(state, move):
                    new_move = copy.deepcopy(move)
                    new_move.append(x)
                    moves.append(new_move)
                moves.pop(i)

        return moves

    def nextState(self, state, move):
        new_tresor_pos = move[-1] if self._hypotheticalValidation(state, move) else state.get("tresor_position")
        return {"current_player": (state.get("current_player") + 1) % self.num_players,
                "tresor_position": new_tresor_pos,
                "agent_position": self._hypotheticalNewPositions(state, move),
                "agent_scores": self._hypotheticalNewScore(state, move),
                "player_agent_associations": state.get("player_agent_associations")
                }

    def previousPlayer(self, state):
        return state.get("current_player") + self.num_players - 1 % self.num_players

    def start(self):
        return {"current_player": 0,
                "tresor_position": 7,
                "agent_position": [0] * self.num_agents,
                "agent_scores": [0] * self.num_agents,
                "player_agent_associations": self._drawAgentCards()
                }

    def _compositions(self, n):
        a = [0 for i in range(n + 1)]
        k = 1
        y = n - 1
        while k != 0:
            x = a[k - 1] + 1
            k -= 1
            while 2 * x <= y:
                a[k] = x
                y -= x
                k += 1
            l = k + 1
            while x <= y:
                a[k] = x
                a[l] = y
                yield a[:k + 2]
                x += 1
                y -= 1
            a[k] = x + y
            y = x + y - 1
            yield a[:k + 1]

    def _drawAgentCards(self):
        random_allocation = random.sample(range(self.num_agents), k=self.num_agents)
        player_agent_association = {}
        players = self.players
        for i in range(1, self.num_agents - self.num_players + 1):
            players += ["Npc{}".format(i)]
        print(players)
        for i, player in enumerate(players):
            player_agent_association.update({player: random_allocation[i]})
        return player_agent_association

    def _hypotheticalNewPositions(self, state, move):
        return [(x + move[i]) % self.board_length for i, x in enumerate(state.get("agent_position"))]

    def _hypotheticalNewScore(self, state, move):
        if self._hypotheticalValidation(state, move):
            new_agent_positions = self._hypotheticalNewPositions(state, move)
            new_scores = []
            for i in range(self.num_agents):
                agent_position = new_agent_positions[i]
                step_size = self.step_sizes.get(agent_position)
                new_scores.append(state.get("agent_scores")[i] + step_size)
            return new_scores
        else:
            return state.get("agent_scores")

    def _hypotheticalNewTresorPositions(self, state, move):
        new_agent_positions = self._hypotheticalNewPositions(state, move)
        valid_tresor_positions = [x for x in range(self.board_length)
                                  if not any(agent_position == x for agent_position in new_agent_positions)]
        return valid_tresor_positions

    def _hypotheticalValidation(self, state, move):
        new_agent_positions = self._hypotheticalNewPositions(state, move)
        return any(x == state.get("tresor_position") for x in new_agent_positions)

    def _rollDice(self):
        return random.choice(range(1, 7))


# Players
players = ["Anna", "Jack", "Kim"]
