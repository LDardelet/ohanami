import curses

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ohanami.game import (
        OCard,
        OGame,
        OPlayer,
    )


@dataclass
class ODisplay:
    CARD_WIDTH = 8
    CARD_HEIGHT = 7

    def __init__(self, game: "OGame") -> None:
        self.game = game
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.size = (curses.LINES, curses.COLS)

        if len(game.players) > 4:
            raise ValueError("Cannot draw a game with more than 4 players.")

    def exit(self) -> None:
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    @classmethod
    def create_card(cls, card: "OCard") -> list[str]:
        internal_width = cls.CARD_WIDTH - 2
        card_str = [f" {'_'*internal_width} "]
        for line in range(cls.CARD_HEIGHT):
            if line == int(cls.CARD_HEIGHT / 2):
                data = str(card.value)
                width = internal_width - len(data)
                card_str += [f"|{' '*int(width/2)+data+' '*int(width/2 + width%2)}|"]
            elif line == int(cls.CARD_HEIGHT / 2) + 1:
                data = str(card.color.value)
                width = internal_width - len(data)
                card_str += [f"|{' '*int(width/2)+data+' '*int(width/2 + width%2)}|"]
            elif line == cls.CARD_HEIGHT - 1:
                card_str += [f"|{'_'*internal_width}|"]
            else:
                card_str += [f"|{' '*internal_width}|"]
        return card_str

    def render(self, player: "OPlayer | None" = None) -> None:
        pass
