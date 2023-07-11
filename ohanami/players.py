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


class BetterBeSafe(OBackend):
    """this player plays the closest card to one of his piles, and do the same for its second card"""

    noob = True

    def play(
        self, cards: "list[OCard]", piles: "tuple[OPile, OPile, OPile]", game: "OGame"
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        # first card
        smallest_distance = 122
        first_card = None
        first_pile_i = None
        for card in cards:
            for i in range(0, 3):  # loop on the 3 piles
                if card.value > piles[i].max:
                    distance = card.value - piles[i].max
                elif card.value < piles[i].min:
                    distance = piles[i].min - card.value
                else:
                    distance = 122
                if distance < smallest_distance:
                    first_card = card
                    first_pile_i = i
        if first_pile_i is None:
            return (
                (None, cards[0]),
                (None, cards[1]),
            )
        assert first_card is not None
        piles[first_pile_i].add(first_card)

        # second card, same thing
        smallest_distance = 122
        second_card = None
        second_pile_i = None
        for card in cards:
            if card is first_card:
                continue
            for i in range(0, 3):
                if card.value > piles[i].max:
                    distance = card.value - piles[i].max
                elif card.value < piles[i].min:
                    distance = piles[i].min - card.value
                else:
                    distance = 122
                if distance < smallest_distance:
                    second_card = card
                    second_pile_i = i

        if second_card is None:
            second_card = next(card for card in cards if card is not first_card)
        # return the two selected cards
        return (
            (first_pile_i, first_card),
            (second_pile_i, second_card),
        )


AVAILABLE_PLAYERS = [RandomRetardPlayer, AlwaysSmall, BetterBeSafe]
