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
