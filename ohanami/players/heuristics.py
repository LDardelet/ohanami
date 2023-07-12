from typing import TYPE_CHECKING

from ohanami.players.base import OBackend

if TYPE_CHECKING:
    from ohanami.game import OCard, OGame, OPile


class AlwaysSmall(OBackend):
    noob = True

    def play(
        self, cards: "list[OCard]", piles: "tuple[OPile, OPile, OPile]", game: "OGame"
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        cards = [card for card in sorted(cards, key=lambda card: card.value)]
        second_card, first_card = cards[:2]
        max_diff, first_pile = (
            122 if piles[0].min < first_card.value else piles[0].min - first_card.value,
            0,
        )
        if (diff := piles[1].min - first_card.value) > 0 and diff < max_diff:
            max_diff, first_pile = diff, 1
        if (diff := piles[2].min - first_card.value) > 0 and diff < max_diff:
            max_diff, first_pile = diff, 2
        if max_diff < 120:
            piles[first_pile].add(first_card)
        max_diff, second_pile = (
            122
            if piles[0].min < second_card.value
            else piles[0].min - second_card.value,
            0,
        )
        if (diff := piles[1].min - second_card.value) > 0 and diff < max_diff:
            max_diff, second_pile = diff, 1
        if (diff := piles[2].min - second_card.value) > 0 and diff < max_diff:
            max_diff, second_pile = diff, 2

        return (
            (first_pile, first_card),
            (second_pile, second_card),
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


class Centrist(OBackend):
    """Plays the centermost (relative to 60) cards playable."""

    def play(
        self, cards: "list[OCard]", piles: "tuple[OPile, OPile, OPile]", game: "OGame"
    ) -> "tuple[tuple[int | None, OCard], tuple[int | None, OCard]]":
        cards = [card for card in sorted(cards, key=lambda card: abs(card.value - 60))]
        selected_cards: list[tuple[int | None, OCard]] = []
        for card in cards:
            best_pile = self.get_closest_pile(card, piles)
            if best_pile is not None:
                selected_cards.append((best_pile, card))
                if len(selected_cards) == 2:
                    return (selected_cards[0], selected_cards[1])
                piles[best_pile].add(card)
        while len(selected_cards) != 2:
            selected_cards.append(
                (
                    None,
                    next(
                        card
                        for card in cards
                        if not any(
                            selected_card is card
                            for selected_pile, selected_card in selected_cards
                        )
                    ),
                )
            )
        return (selected_cards[0], selected_cards[1])
