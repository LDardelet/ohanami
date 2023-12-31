import random

from typing import TYPE_CHECKING

from ohanami.players.base import OBackend

if TYPE_CHECKING:
    from ohanami.game import OCard, OGame, OPile


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
