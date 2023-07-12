"""Ohanami game core module."""
from copy import deepcopy
from dataclasses import (
    dataclass,
    field,
)
from enum import Enum
import random

from ohanami.players import (
    AVAILABLE_PLAYERS,
    OBackend,
)
from ohanami.display import ODisplay


class OColor(Enum):
    WATER: str = "water"
    LEAF: str = "leaf"
    STONE: str = "stone"
    SAKURA: str = "sakura"


class OSeason(Enum):
    FIRST: int = 0
    SECOND: int = 1
    THIRD: int = 2


# fmt: off
DECK = {
    OColor.WATER: [
        2, 4, 8, 10, 16, 20, 22, 26, 32, 34, 38, 40, 44, 46, 50, 52, 58,
        62, 64, 68, 74, 76, 80, 82, 86, 88, 92, 94, 100, 104, 106, 110, 116, 118
    ],
    OColor.LEAF: [
        3, 6, 9, 12, 15, 18, 24, 27, 30, 33, 36, 39, 45, 48, 51, 54, 57, 60,
        66, 69, 72, 75, 78, 81, 87, 90, 93, 96, 99, 102, 108, 111, 114, 117, 120
    ],
    OColor.STONE: [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98, 105, 112, 119],
    OColor.SAKURA: [
        1, 5, 11, 13, 17, 19, 23, 25, 29, 31, 37, 41, 43, 47, 53, 55, 59,
        61, 65, 67, 71, 73, 79, 83, 85, 89, 95, 97, 101, 103, 107,  109, 113, 115
    ],
}
# fmt: on


@dataclass
class OCard:
    value: int
    color: OColor


@dataclass
class OPile:
    cards: list[OCard] = field(default_factory=list)

    @property
    def min(self) -> int:
        """Return the minimum value of a pile.

        Returns 121 if not card in the pile."""
        if not self.cards:
            return 121
        return self.cards[0].value

    @property
    def max(self) -> int:
        """Return the maximum value of a pile.

        Returns 0 if not card in the pile."""
        if not self.cards:
            return 0
        return self.cards[-1].value

    def get_color(self, color: OColor) -> int:
        """Get the number of cards of a certain type."""
        return len([card for card in self.cards if card.color is color])

    def get_scores(self, season: OSeason) -> dict[OColor, int]:
        """Get the score for a certain season."""
        scores = {OColor.WATER: 3 * self.get_color(OColor.WATER)}
        if season is OSeason.SECOND or season is OSeason.THIRD:
            scores[OColor.LEAF] = 4 * self.get_color(OColor.LEAF)
        if season is OSeason.THIRD:
            scores[OColor.STONE] = 7 * self.get_color(OColor.STONE)
            scores[OColor.SAKURA] = sum(
                [i for i in range(1, self.get_color(OColor.SAKURA) + 1)]
            )
        return scores

    def add(self, card: OCard, backend: "OBackend | None" = None) -> bool:
        """Add a card to this pile.

        Returns:
            True if able to add, False otherwise.
        """
        if not self.cards:
            self.cards.append(card)
            print(f"-Added new pile with card {card}")
            return True
        if card.value < self.min:
            print(f"-Added card {card} to pile {self.min} -> {self.max}")
            self.cards.insert(0, card)
        elif card.value > self.max:
            print(f"-Added card {card} to pile {self.min} -> {self.max}")
            self.cards.append(card)
        else:
            if backend is not None and backend.noob:
                print(f"-Throwing card {card} (noob).")
                return False
            raise ValueError(
                f"Card {card.value} cannot be placed in pile {', '.join([str(card.value) for card in self.cards])} ({backend.__class__.__name__})."
            )
        return True


@dataclass
class OPlayer:
    """Class defining a player."""

    backend: "OBackend"
    name: str
    discarded_cards: list[OCard] = field(default_factory=list)
    scores: list[dict[OColor, int]] = field(
        default_factory=lambda: [
            {OColor.WATER: 0, OColor.LEAF: 0, OColor.STONE: 0, OColor.SAKURA: 0}
            for _ in range(3)
        ]
    )
    piles: tuple[OPile, OPile, OPile] = field(
        default_factory=lambda: (OPile(), OPile(), OPile())
    )
    hand: list[OCard] = field(default_factory=list)

    @property
    def score(self) -> int:
        return sum([sum(turn.values()) for turn in self.scores])

    def play(self, game: "OGame") -> None:
        played_cards = self.backend.play(list(self.hand), deepcopy(self.piles), game)
        for npile, played_card in played_cards:
            print(played_card, self.hand)
            card = next(card for card in self.hand if card.value == played_card.value)
            self.hand.remove(card)
            if npile is None:
                print(f"-Throwing card {card}")
                self.discarded_cards.append(card)
                continue
            pile = self.piles[npile]
            if not pile.add(card, backend=self.backend):
                self.discarded_cards.append(card)


@dataclass
class OGame:
    """Class defining an ohanami game."""

    display: ODisplay | None
    players: list[OPlayer]
    finished: bool = False
    current_player: OPlayer | None = None
    current_turn: int = 0
    current_season: OSeason = OSeason.FIRST
    remaining_deck: list[OCard] = field(default_factory=list)

    @classmethod
    def create(cls, players: "list[OBackend | None]") -> "OGame":
        """Create a new game."""
        game = cls(None, [])
        deck = create_deck()
        random.shuffle(deck)
        for backend in players:
            if backend is None:
                backend = random.choice(AVAILABLE_PLAYERS)()
            ID = 1
            name = f"{backend.__class__.__name__}_{ID}"
            while (
                next((player for player in game.players if player.name == name), None)
                is not None
            ):
                ID += 1
                name = f"{backend.__class__.__name__}_{ID}"
            game.players.append(OPlayer(backend, name, hand=deck[:10]))
            deck = deck[10:]
        game.remaining_deck = deck
        random.shuffle(game.players)
        return game

    def start(self) -> None:
        if self.display:
            self.display.main()
            return
        print(f"Starting at season {self.current_season}")
        while not self.finished:
            self.turn()

    def turn(self) -> None:
        """Run a complete turn."""
        if self.current_player is None:
            self.current_player = self.players[0]
        self.current_turn += 1
        for player in self.players:
            print(f"{player.name} is playing.")
            player.play(self)
        if self.current_season is OSeason.SECOND:
            hand = self.players[0].hand
            for player in reversed(self.players):
                player.hand, hand = hand, player.hand
        else:
            hand = self.players[-1].hand
            for player in self.players:
                player.hand, hand = hand, player.hand
        if self.current_turn == 5:
            self.go_next_season()

    def go_next_season(self) -> None:
        for player in self.players:
            for pile in player.piles:
                for color, score in pile.get_scores(self.current_season).items():
                    player.scores[self.current_season.value][color] += score
        self.current_turn = 0
        match self.current_season:
            case OSeason.FIRST:
                self.current_season = OSeason.SECOND
                print()
                print(f"# Switching to season {self.current_season}")
                for player in self.players:
                    player.hand = self.remaining_deck[:10]
                    self.remaining_deck = self.remaining_deck[10:]
            case OSeason.SECOND:
                self.current_season = OSeason.THIRD
                print()
                print(f"# Switching to season {self.current_season}")
                for player in self.players:
                    player.hand = self.remaining_deck[:10]
                    self.remaining_deck = self.remaining_deck[10:]
            case OSeason.THIRD:
                self.conclude()

    def conclude(self) -> None:
        print()
        print("# Concluding")
        self.finished = True
        self.display_scores()

    def display_scores(self) -> None:
        data = {}
        max_score = max([player.score for player in self.players])
        for player in self.players:
            name = f"*{player.name}" if player.score == max_score else player.name
            data[name] = [
                f"{player.scores[0][OColor.WATER]:2d}",
                f"{player.scores[1][OColor.WATER]:2d}/{player.scores[1][OColor.WATER]:2d}",
                (
                    f"{player.scores[2][OColor.WATER]:2d}/{player.scores[2][OColor.WATER]:3d}"
                    f"/{player.scores[2][OColor.STONE]:3d}/{player.scores[2][OColor.SAKURA]:3d}"
                ),
                f"={player.score}",
                f"x{len(player.discarded_cards)} cards",
            ]
        names_width = 0
        col_widths = [0 for _ in range(len(list(data.values())[0]))]
        for name, columns in data.items():
            names_width = max(names_width, len(name)) + 1
            for n_col, column in enumerate(columns):
                col_widths[n_col] = max(col_widths[n_col], len(column))
        lines = ["_" * (1 + names_width + 1)]
        for col_width in col_widths:
            lines[-1] += "_" * (col_width + 1)
        for name, columns in data.items():
            lines += [f"|{{0:{names_width}}}|".format(name)]
            for column, col_width in zip(columns, col_widths):
                lines[-1] += f"{{0:{col_width}}}|".format(column)
        lines += ["|" + "_" * names_width + "|"]
        for col_width in col_widths:
            lines[-1] += "_" * col_width + "|"
        print("\n".join(lines))


def create_deck() -> list[OCard]:
    """Create the deck of cards."""
    cards = []
    for color, values in DECK.items():
        cards += [OCard(value, color) for value in values]
    return cards
