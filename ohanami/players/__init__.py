from ohanami.players.base import OBackend
from ohanami.players.heuristics import (
    AlwaysSmall,
    BetterBeSafe,
)
from ohanami.players.random import RandomRetardPlayer

AVAILABLE_PLAYERS = [RandomRetardPlayer, AlwaysSmall, BetterBeSafe]
