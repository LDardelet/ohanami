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
    HEIGHT: int
    WIDTH: int

    CARD_HEIGHT = 7
    CARD_WIDTH = 8

    PLAYER_HEIGHT = 20
    PLAYER_WIDTH = 50

    def __init__(self, game: "OGame") -> None:
        self.game = game
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

        self.HEIGHT = curses.LINES
        self.WIDTH = curses.COLS

        self.center = (int(self.HEIGHT / 2), int(self.WIDTH))

        if len(game.players) > 4:
            raise ValueError("Cannot draw a game with more than 4 players.")

        self.center_window = curses.newwin(
            int(self.HEIGHT / 2),
            int(self.WIDTH / 2),
            int(self.HEIGHT / 4),
            int(self.WIDTH / 4),
        )
        self.players_windows: list[curses._CursesWindow] = []
        for n_player, player in enumerate(self.game.players):
            match n_player:
                case 0:
                    self.players_windows.append(
                        curses.newwin(
                            self.PLAYER_HEIGHT,
                            self.PLAYER_WIDTH,
                            0,
                            int((self.WIDTH - self.PLAYER_WIDTH) / 2),
                        )
                    )
                case 1:
                    self.players_windows.append(
                        curses.newwin(
                            self.PLAYER_WIDTH,
                            self.PLAYER_HEIGHT,
                            int((self.HEIGHT - self.PLAYER_WIDTH) / 2),
                            self.WIDTH - self.PLAYER_HEIGHT,
                        )
                    )
                case 2:
                    self.players_windows.append(
                        curses.newwin(
                            self.PLAYER_HEIGHT,
                            self.PLAYER_WIDTH,
                            int(self.HEIGHT - self.PLAYER_HEIGHT),
                            int((self.WIDTH - self.PLAYER_WIDTH) / 2),
                        )
                    )
                case 3:
                    self.players_windows.append(
                        curses.newwin(
                            self.PLAYER_WIDTH,
                            self.PLAYER_HEIGHT,
                            int((self.HEIGHT - self.PLAYER_WIDTH) / 2),
                            0,
                        )
                    )
            self.players_windows[-1].addch(str(n_player))
            self.players_windows[-1].refresh()

        self.stdscr.addstr(int(self.HEIGHT / 2), int(self.WIDTH / 2), "OHANAMI")
        self.stdscr.refresh()

    def main(self) -> None:
        while True:
            c = self.stdscr.getch()
            if c == ascii.ESC:
                print("here")
                self.exit()
                break
            if c == ord("t"):
                self.game.turn()

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
