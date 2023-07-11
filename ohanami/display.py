import curses

from curses import ascii

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

        self.center = (int(curses.LINES / 2), int(curses.COLS))

        if len(game.players) > 4:
            raise ValueError("Cannot draw a game with more than 4 players.")

        self.center_window = curses.newwin(
            int(curses.LINES / 2),
            int(curses.COLS / 2),
            int(curses.LINES / 4),
            int(curses.COLS / 4),
        )
        self.players_windows: list[curses._CursesWindow] = []
        for n_player, player in enumerate(self.game.players):
            width = 30
            height = 12
            match n_player:
                case 0:
                    self.players_windows.append(
                        curses.newwin(
                            height,
                            width,
                            0,
                            int((curses.COLS - width) / 2),
                        )
                    )
                case 1:
                    self.players_windows.append(
                        curses.newwin(
                            width,
                            height,
                            int((curses.LINES - width) / 2),
                            curses.COLS - height,
                        )
                    )
                case 2:
                    self.players_windows.append(
                        curses.newwin(
                            height,
                            width,
                            int(curses.LINES - height),
                            int((curses.COLS - width) / 2),
                        )
                    )
                case 3:
                    self.players_windows.append(
                        curses.newwin(
                            width,
                            height,
                            int((curses.LINES - width) / 2),
                            0,
                        )
                    )
            height, width = self.players_windows[-1].getmaxyx()
            self.players_windows[-1].addstr(0, int(width / 2), player.name)
            self.players_windows[-1].refresh()

        self.main()

    def main(self) -> None:
        while True:
            c = self.stdscr.getch()
            if c == ascii.ESC:
                self.exit()

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
