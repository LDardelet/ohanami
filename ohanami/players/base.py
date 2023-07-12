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

    @staticmethod
    def get_closest_pile(
        card: "OCard", piles: "tuple[OPile, OPile, OPile]", sign: int = 0
    ) -> int | None:
        """Get the closest admissible pile for this card.

        Args:
            card: Card to compare.
            piles: Tuple of piles.
            sign: If positive, only places the card at the top of the pile.
                  If negative, only places the card at the bottom of the pile.
                  If 0, all combinations are considered.

        Returns:
            The index of the best admissible pile, None of no admissible pile.
        """
        best_pile = None
        max_diff = 120
        for n_pile, pile in enumerate(piles):
            if not pile.cards:  # empty piles are the best
                return n_pile
            if sign <= 0:
                diff = pile.min - card.value
                if diff > 0 and diff < max_diff:
                    max_diff, best_pile = diff, n_pile
            if sign >= 0:
                diff = card.value - pile.max
                if diff > 0 and diff < max_diff:
                    max_diff, best_pile = diff, n_pile
        return best_pile
