import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ohanami.game import OCard, OGame, OPile


class OBackend:
    # If True, registers a card placed on an invalid deck as a discard
    noob: bool = False

    def play(
        self,
        cards: "list[OCard]",
        piles: "tuple[OPile, OPile, OPile]",
        game: "OGame",
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        raise NotImplementedError


class RandomRetardPlayer(OBackend):
    noob = True

    def play(
        self, cards: "list[OCard]", piles: "tuple[OPile, OPile, OPile]", game: "OGame"
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        first_card = random.choice(cards)
        cards = [card for card in cards if card is not first_card]
        return (
            (random.randint(0, 2), first_card),
            (random.randint(0, 2), random.choice(cards)),
        )


class AlwaysSmall(OBackend):
    noob = True

    def play(
        self, cards: "list[OCard]", piles: "tuple[OPile, OPile, OPile]", game: "OGame"
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        cards = [card for card in sorted(cards, key=lambda card: card.value)]
        return (
            (random.randint(0, 2), cards[1]),
            (random.randint(0, 2), cards[0]),
        )


AVAILABLE_PLAYERS = [RandomRetardPlayer, AlwaysSmall]
