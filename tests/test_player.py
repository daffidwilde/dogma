"""Tests for the player classes."""

from hypothesis import given
from hypothesis.strategies import text

from dogma import Player


@given(name=text())
def test_base_init(name):
    """Test that the abstract base player class can be instantiated."""

    player = Player(name)

    assert player.name == name
    assert player.role is None
    assert player.partner is None
    assert player.seen is None
    assert player.denounced is False


@given(name=text())
def test_base_repr(name):
    """Test the string representation of a player instance."""

    player = Player(name)
    representation = str(player)

    assert representation == f"Player({name}, None, False)"
