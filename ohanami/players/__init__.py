from ohanami.players.base import OBackend
from ohanami.players.heuristics import (
    AlwaysSmall,
    BetterBeSafe,
    Centrist,
)
from ohanami.players.random import RandomRetardPlayer

AVAILABLE_PLAYERS: list[type[OBackend]] = [
    RandomRetardPlayer,
    AlwaysSmall,
    BetterBeSafe,
    Centrist,
]
