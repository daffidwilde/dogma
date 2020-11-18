""" Standard and custom strategies for hypothesis tests. """

import random

from hypothesis.strategies import composite, integers, lists, text

from dogma import DogmaGame, RandomPlayer

seeds = integers(min_value=0, max_value=1000)
names = lists(text(), unique=True, min_size=5, max_size=6)


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

    return [RandomPlayer(name) for name in draw(names)]


@composite
def games(draw):
    """A custom strategy for creating game instances."""

    return DogmaGame(draw(players()), draw(seeds))
