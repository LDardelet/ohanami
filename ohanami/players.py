import random

from ohanami.game import OBackend, OCard, OGame, OPiles


class RandomRetardPlayer(OBackend):
    noob = True

    def play(
        self, cards: list[OCard], piles: OPiles, game: OGame
    ) -> tuple[tuple[int | None, OCard], tuple[int | None, OCard]]:
        first_card = random.choice(cards)
        cards = [card for card in cards if card is not first_card]
        return (
            (random.randint(0, 2), first_card),
            (random.randint(0, 2), random.choice(cards)),
        )
