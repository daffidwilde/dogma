"""Tests for the player classes."""

import random
from collections import Counter

from hypothesis import given
from hypothesis.strategies import text

from dogma import BasePlayer, RandomPlayer

from .util import decks, players, seeds


@given(name=text())
def test_base_init(name):
    """Test that the abstract base player class can be instantiated."""

    player = BasePlayer(name)

    assert player.name == name
    assert player.role is None
    assert player.partner is None
    assert player.seen is None
    assert player.denounced is False


@given(name=text())
def test_base_repr(name):
    """Test the string representation of a player instance."""

    player = BasePlayer(name)
    representation = str(player)

    assert representation == f"BasePlayer({name}, None, False)"


@given(seed=seeds, players_=players())
def test_random_nominate(seed, players_):
    """Test that a random player nominates successfully."""

    random.seed(seed)

    player, ex_dean, ex_editor = players_[:3]
    nomination = player.nominate(players_[3:])

    assert nomination not in (player, ex_dean, ex_editor)


@given(name=text(), seed=seeds)
def test_random_vote(name, seed):
    """Test that a random player votes successfully."""

    random.seed(seed)
    player = RandomPlayer(name)

    assert player.vote("foo") in ("yes", "no")


@given(name=text(), seed=seeds, deck=decks())
def test_random_choose_cards_to_submit_without_overrule(name, seed, deck):
    """Test that a random player can play a hand without the overrule power."""

    random.seed(seed)
    player = RandomPlayer(name)
    hand = deck[:3]

    choices, reject, overrule = player.choose_cards_to_submit(hand)
    assert len(choices) == 2
    assert Counter(choices + [reject]) == Counter(deck[:3])
    assert reject in ("H", "G")
    assert overrule is False


@given(name=text(), seed=seeds)
def test_random_agree_to_overrule(name, seed):
    """Test that a random player can decide whether to agree to an overrule."""

    random.seed(seed)
    player = RandomPlayer(name)

    assert player.agree_to_overrule() in (True, False)


@given(seed=seeds, players_=players())
def test_random_denounce(seed, players_):
    """Test that a random player can denounce another player."""

    random.seed(seed)
    player = players_[0]
    denounced_player = player.denounce(players_[1:])

    assert denounced_player in players_[1:]
    assert denounced_player is not player
