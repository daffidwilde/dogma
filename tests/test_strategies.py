""" Tests for the strategy classes. """

import random
from collections import Counter

from hypothesis import given

from dogma import Player

from .util import decks, playergroups, players, seeds


@given(seed=seeds, group=playergroups())
def test_nominate(seed, group):
    """Test that a player can nominate successfully from a group."""

    random.seed(seed)

    player, ex_dean, ex_editor = group[:3]
    nomination = player.nominate(group[3:])

    assert isinstance(nomination, Player)
    assert nomination in group
    assert nomination not in (player, ex_dean, ex_editor)


@given(player=players())
def test_vote(player):
    """Test that a player votes successfully."""

    assert player.vote("foo") in ("yes", "no")


@given(player=players(), deck=decks())
def test_choose_cards_to_submit_without_overrule(player, deck):
    """Test that a player can play a hand without the overrule power."""

    hand = deck[:3]

    choices, reject, overrule = player.choose_cards_to_submit(hand)
    assert len(choices) == 2
    assert Counter(choices + [reject]) == Counter(deck[:3])
    assert reject in ("H", "G")
    assert overrule is False


@given(player=players())
def test_agree_to_overrule(player):
    """Test that a player can decide whether to agree to an overrule."""

    assert player.agree_to_overrule() in (True, False)


@given(group=playergroups())
def test_random_denounce(group):
    """Test that a player can denounce another player."""

    player = group[0]
    denounced_player = player.denounce(group[1:])

    assert isinstance(denounced_player, Player)
    assert denounced_player in group[1:]
    assert denounced_player is not player
