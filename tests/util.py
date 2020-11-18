""" Standard and custom strategies for hypothesis tests. """

import random

from hypothesis.strategies import composite, integers, lists, sampled_from, text

from dogma import DogmaGame
from dogma.strategies import all_strategies

seeds = integers(min_value=0, max_value=1000)
names = lists(text(), unique=True, min_size=5, max_size=6)
strategies = lists(sampled_from(all_strategies), min_size=5, max_size=6)


@composite
def decks(draw, state=None, number_of_helio=11, number_of_geo=6):
    """A custom strategy for creating a shuffled deck."""

    if state is None:
        state = random.Random(draw(seeds))

    deck = ["H"] * number_of_helio + ["G"] * number_of_geo

    state.shuffle(deck)
    return deck


@composite
def players(draw):
    """A custom strategy for creating player instances."""

    Strategy = draw(sampled_from(all_strategies))
    name = draw(text())

    return Strategy(name)


@composite
def playergroups(draw):
    """A custom strategy for creating groups of player instances."""

    player_names = draw(names)
    player_strategies = draw(strategies)
    return [
        strategy(name)
        for strategy, name in zip(player_strategies, player_names)
    ]


@composite
def games(draw):
    """A custom strategy for creating game instances."""

    return DogmaGame(draw(playergroups()), draw(seeds))
