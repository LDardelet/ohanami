# type: ignore
import argparse
import sys

import numpy as np

from matplotlib import pyplot as plt

from ohanami.game import OGame
from ohanami.players import AVAILABLE_PLAYERS, OBackend


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="tournament")
    parser.add_argument("--turns", type=int, default=100)
    parser.add_argument("--sets-per-turn", type=int, default=10)
    parser.add_argument("--players", type=int, choices=[3, 4], default=4)

    tournament = parser.parse_args(argv[1:])
    print(
        f"Starting tounament with {tournament.turns} turns, {tournament.sets_per_turn} sets per turns."
    )

    scores: dict[type[OBackend], list[int]] = {
        backend: [] for backend in AVAILABLE_PLAYERS
    }

    NPOINTS = 100
    plt.ion()
    f, ax = plt.subplots(1, 1)
    ax.set_xlim(0, 220)
    ax.set_ylim(-0.05, 1.05)
    plots = {
        backend: ax.plot(
            np.linspace(0, 220, NPOINTS),
            np.linspace(0, 0, NPOINTS),
            label=backend.__name__,
        )[0]
        for backend in AVAILABLE_PLAYERS
    }
    ax.legend(loc="upper left")
    plt.plot()
    plt.pause(0.01)

    for turn in range(tournament.turns):
        print(f"Turn {turn+1}/{tournament.turns}")
        game = OGame.create([None for i in range(tournament.players)])
        for _ in range(tournament.sets_per_turn):
            game.reset()
            game.start()
            for player in game.players:
                scores[player.backend.__class__].append(player.score)
        for backend, score in scores.items():
            xs, ys = get_distribution(score)
            plots[backend].set_data(xs, ys / max(0.0001, ys.max()))
        plt.draw()
        plt.pause(0.01)
    print(scores)
    input("hit enter")


def get_distribution(
    scores: list[int], npoints=100, sigma_limit=5
) -> tuple[np.ndarray[float], np.ndarray[float]]:
    """Get the equivalent normal distribution from a series of scores."""
    mean = np.mean(scores)
    dev = np.std(scores)
    xs = np.linspace(mean - 5 * dev, mean + 5 * dev, npoints)
    ys = np.e ** (-((xs - mean) ** 2) / dev**2) / (dev * np.sqrt(2 * np.pi))
    return xs, ys


if __name__ == "__main__":
    main(sys.argv)
