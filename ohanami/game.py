"""Ohanami game core module."""
from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import (
    dataclass,
    field,
)
from enum import Enum
import random


class OColor(Enum):
    WATER: str = "water"
    LEAF: str = "leaf"
    STONE: str = "stone"
    SAKURA: str = "sakura"


class OSeason(Enum):
    FIRST: int = 1
    SECOND: int = 2
    THIRD: int = 3


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
class OPiles:
    @staticmethod
    def create_pile() -> tuple[list[OCard], list[OCard], list[OCard]]:
        return ([], [], [])

    piles: tuple[list[OCard], list[OCard], list[OCard]] = field(
        default_factory=create_pile
    )

    def __getitem__(self, index: int) -> list[OCard]:
        return self.piles[index]

    def get_color(self, color: OColor) -> int:
        """Get the number of cards of a certain type."""
        n_cards = 0
        for pile in self.piles:
            n_cards += len([card for card in pile if card.color is color])
        return n_cards

    def get_score(self, season: OSeason) -> int:
        """Get the score for a certain season."""
        match season:
            case OSeason.FIRST:
                return 3 * self.get_color(OColor.WATER)
            case OSeason.SECOND:
                return 3 * self.get_color(OColor.WATER) + 4 * self.get_color(
                    OColor.LEAF
                )
            case OSeason.THIRD:
                return (
                    3 * self.get_color(OColor.WATER)
                    + 4 * self.get_color(OColor.LEAF)
                    + 7 * self.get_color(OColor.STONE)
                    + sum([i for i in range(1, self.get_color(OColor.SAKURA) + 1)])
                )


@dataclass
class OPlayer:
    """Class defining a player."""

    backend: "OBackend"
    name: str
    score: int = 0
    piles: OPiles = field(default_factory=lambda: OPiles())
    hand: list[OCard] = field(default_factory=list)

    def play(self, game: "OGame") -> None:
        played_cards = self.backend.play(list(self.hand), self.piles, game)
        for npile, card in played_cards:
            self.hand.remove(card)
            if npile is None:
                print(f"Throwing card {card}")
                game.discarded_cards.append(card)
                continue
            pile = self.piles[npile]
            if not pile:
                pile.append(card)
                print(f"Added new pile with card {card}")
            else:
                if card.value < pile[0].value:
                    print(
                        f"Added card {card} to pile {pile[0].value} -> {pile[-1].value}"
                    )
                    pile.insert(0, card)
                elif card.value > pile[-1].value:
                    print(
                        f"Added card {card} to pile {pile[0].value} -> {pile[-1].value}"
                    )
                    pile.append(card)
                else:
                    if self.backend.noob:
                        print(f"Throwing card {card} (noob).")
                        game.discarded_cards.append(card)
                        continue
                    raise ValueError(
                        f"Card {card} cannot be placed in pile {', '.join([str(card) for card in pile])}."
                    )


@dataclass
class OGame:
    """Class defining an ohanami game."""

    players: list[OPlayer]
    current_player: OPlayer | None = None
    current_turn: int = 0
    current_season: OSeason = OSeason.FIRST
    remaining_deck: list[OCard] = field(default_factory=list)
    discarded_cards: list[OCard] = field(default_factory=list)

    @classmethod
    def create(cls, players: "list[OBackend]") -> "OGame":
        """Create a new game."""
        game = cls([])
        deck = create_deck()
        random.shuffle(deck)
        for backend in players:
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
            player.score += player.piles.get_score(self.current_season)
        match self.current_season:
            case OSeason.FIRST:
                self.current_season = OSeason.SECOND
                for player in self.players:
                    player.hand = self.remaining_deck[:10]
                    self.remaining_deck = self.remaining_deck[10:]
            case OSeason.SECOND:
                self.current_season = OSeason.THIRD
                for player in self.players:
                    player.hand = self.remaining_deck[:10]
                    self.remaining_deck = self.remaining_deck[10:]
            case OSeason.THIRD:
                self.conclude()

    def conclude(self) -> None:
        pass


def create_deck() -> list[OCard]:
    """Create the deck of cards."""
    cards = []
    for color, values in DECK.items():
        cards += [OCard(value, color) for value in values]
    return cards


class OBackend(ABC):
    # If True, registers a card placed on an invalid deck as a discard
    noob: bool = False

    @abstractmethod
    def play(
        self,
        cards: list[OCard],
        piles: OPiles,
        game: OGame,
    ) -> tuple[tuple[int | None, OCard], tuple[int | None, OCard]]:
        raise NotImplementedError
