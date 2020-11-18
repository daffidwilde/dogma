""" Tests for the DogmaGame class. """

from collections import Counter

from hypothesis import assume, given
from hypothesis.strategies import booleans, integers

from dogma import DogmaGame

from .util import games, players, seeds


@given(players_=players(), seed=seeds)
def test_init(players_, seed):
    """Test that a game instance can be made."""

    game = DogmaGame(players_, seed)

    assert game.players == players_
    assert game.seed == seed
    assert game.winner is None
    assert game.message is None

    count = Counter(game.journal_cards)
    assert count == {"H": 11, "G": 6}
    assert game.discard_pile == []

    assert game.publications == {"H": 0, "G": 0}
    assert game.last_successfully_published is None
    assert game.pressure_to_print == 0
    assert game.overrule_available is False

    assert game.galileo is None
    assert game.maverick is None
    assert game.dean is None
    assert game.editor is None
    assert game.ex_dean is None
    assert game.ex_editor is None


@given(game=games())
def test_shuffle_roles(game):
    """Test that a game instance can shuffle its role cards."""

    roles = game.shuffle_roles()
    count = Counter(roles)

    number_of_players = len(game.players)
    assert count == {"C": number_of_players - 2, "M": 1, "G": 1}


@given(game=games())
def test_assign_roles(game):
    """Test that a game instance can assign and record its roles."""

    game.assign_roles()
    assigned_roles = [player.role for player in game.players]
    count = Counter(assigned_roles)

    number_of_players = len(game.players)
    assert count == {"C": number_of_players - 2, "M": 1, "G": 1}

    galileo = next(player for player in game.players if player.role == "G")
    assert game.galileo is galileo

    maverick = next(player for player in game.players if player.role == "M")
    assert game.maverick is maverick


@given(game=games())
def test_inform_mavericks(game):
    """Test that a game instance can reveal the maverick players to one
    another."""

    game.assign_roles()
    galileo = game.galileo
    maverick = game.maverick

    game.inform_mavericks()

    assert galileo.partner is maverick
    assert maverick.partner is galileo


@given(game=games())
def test_elect_first_dean(game):
    """Test that a game instance can select an initial dean."""

    game.elect_first_dean()
    assert game.dean in game.players


@given(game=games())
def test_set_next_dean(game):
    """Test that a game instance can move onto the next available dean."""

    game.dean = game.players[0]
    game.set_next_dean()
    assert game.players.index(game.dean) == 1

    game.players[2].denounced = True
    game.set_next_dean()
    assert game.players.index(game.dean) == 3


@given(game=games())
def test_set_next_dean_loop_around(game):
    """Test that the next dean can set to the start again from the end of the
    player list."""

    game.dean = game.players[-1]
    game.set_next_dean()
    assert game.players.index(game.dean) == 0


@given(game=games())
def test_get_players_for_nomination(game):
    """Test that a game instance only offers the correct players to be
    nominated."""

    game.dean, game.ex_dean, game.ex_editor = game.players[:3]
    potential_nominees = game._get_players_for_nomination()

    assert sum(p.denounced for p in potential_nominees) == 0
    assert sorted(set(potential_nominees), key=lambda p: p.name) == sorted(
        potential_nominees, key=lambda p: p.name
    )

    assert game.dean not in potential_nominees
    assert game.ex_editor not in potential_nominees
    if len(game.players) == 6:
        assert game.ex_dean not in potential_nominees


@given(game=games())
def test_form_print_team(game):
    """Test that a game instance can request a nomination from their dean."""

    game.dean = game.players[0]
    game.ex_dean, game.ex_editor = game.players[-2:]
    nomination = game.form_print_team()

    assert nomination in game.players
    assert nomination not in [game.dean, game.ex_editor]
    if len(game.players) == 6:
        assert nomination is not game.ex_dean


@given(game=games())
def test_cast_vote(game):
    """Test that a game instance can call a vote on a nominee."""

    nominee = game.players[0]
    result = game.cast_vote(nominee)

    if result is True:
        assert game.pressure_to_print == 0
    else:
        assert game.pressure_to_print == 1


@given(game=games())
def test_draw_journals(game):
    """Test that a game instance can draw a hand from the top of the deck, and
    shuffles them if need be."""

    cards = game.journal_cards[:]
    hand = game.draw_journals()
    assert len(hand) == 3
    assert game.journal_cards == cards[3:]

    game.journal_cards = cards[-2:]
    game.discard_pile = cards[:-2]
    hand = game.draw_journals()
    assert len(hand) == 3
    assert len(game.journal_cards) == len(cards) - 3
    assert game.discard_pile == []


@given(game=games())
def test_form_publication_without_overrule(game):
    """Test that a game instance can facilitate the formation of a journal
    without the ability to overrule a selection of cards."""

    game.dean, game.editor = game.players[:2]
    assert game.form_publication()
    assert len(game.discard_pile) == 2
    assert sum(game.publications.values()) == 1
    assert game.last_successfully_published == next(
        team for team, count in game.publications.items() if count > 0
    )
    assert game.pressure_to_print == 0
    assert game.ex_dean is game.dean
    assert game.ex_editor is game.editor


@given(game=games())
def test_form_publication_with_overrule(game):
    """Test that a game instance can facilitate the formation of a journal
    with the ability to overrule a selection of cards."""

    game.dean, game.editor = game.players[:2]
    game.overrule_available = True
    result = game.form_publication()

    if result:
        assert len(game.discard_pile) == 2
        assert sum(game.publications.values()) == 1
        assert game.last_successfully_published == next(
            team for team, count in game.publications.items() if count > 0
        )
        assert game.pressure_to_print == 0
        assert game.ex_dean is game.dean
        assert game.ex_editor is game.editor

    else:
        assert len(game.discard_pile) == 1
        assert sum(game.publications.values()) == 0
        assert game.last_successfully_published is None
        assert game.pressure_to_print == 1
        assert game.ex_dean is None
        assert game.ex_editor is None


@given(game=games())
def test_emergency_publication(game):
    """Test that a game instance can publish an emergency journal and reset
    itself."""

    game.pressure_to_print = 1234567890
    game.last_successfully_published = "foo"
    game.emergency_publication()

    assert sum(game.publications.values()) == 1
    assert game.last_successfully_published is None
    assert game.pressure_to_print == 0


@given(game=games())
def test_perform_emergency_actions_peek(game):
    """Test that a game instance can perform its actions when the mavericks have
    published three journals."""

    game.publications["H"] = 3
    game.dean = game.players[0]
    cards = game.journal_cards[:]
    assert not game.perform_emergency_actions()
    assert game.journal_cards == cards
    assert game.dean.seen == cards[:3]
    assert game.overrule_available is False


@given(game=games())
def test_get_players_for_denouncement(game):
    """Test that a game instance only offers the correct players for
    denouncement."""

    game.dean = game.players[0]
    for player in game.players[-2:]:
        player.denounced = True

    potential_denouncees = game._get_players_for_denouncement()

    assert game.dean not in potential_denouncees
    assert sum(p.denounced for p in potential_denouncees) == 0
    assert set(potential_denouncees) == set(game.players[1:-2])
    assert sorted(set(potential_denouncees), key=lambda p: p.name) == sorted(
        potential_denouncees, key=lambda p: p.name
    )


@given(game=games())
def test_perform_emergency_actions_denounce(game):
    """Test that a game instance can facilitate the denouncing of another player
    by the dean. If that player is Galileo, the game ends."""

    game.assign_roles()
    game.dean = game.players[0]
    game.publications["H"] = 4
    result = game.perform_emergency_actions()

    denounced_player = next(p for p in game.players if p.denounced)
    denounced_status = [p.denounced for p in game.players]
    assert sum(denounced_status) == 1
    assert denounced_status.index(True) == game.players.index(denounced_player)
    assert (denounced_player is game.galileo) is result


@given(game=games())
def test_perform_emergency_actions_denounce_and_overrule(game):
    """Test that a game instance can facilitate a denouncing, and offer up the
    power to overrule. If the denounced player is Galileo, the game ends without
    the overrule being set."""

    game.assign_roles()
    game.dean = game.players[0]
    game.publications["H"] = 5
    result = game.perform_emergency_actions()

    denounced_player = next(p for p in game.players if p.denounced)
    denounced_status = [p.denounced for p in game.players]
    assert sum(denounced_status) == 1
    assert denounced_status.index(True) == game.players.index(denounced_player)
    assert (denounced_player is game.galileo) is result
    assert game.overrule_available is not result


@given(game=games(), publications=integers(min_value=0, max_value=6))
def test_galileo_editor_win(game, publications):
    """Test that a game instance concludes with a maverick win if Galileo is
    made editor with at least three favourable journals published."""

    game.assign_roles()
    game.publications["H"] = publications
    game.editor = game.galileo
    result = game.galileo_editor_win()

    if result:
        assert game.winner == "M"
        assert "rhetorical prowess" in game.message

    else:
        assert game.winner is None
        assert game.message is None


@given(
    game=games(),
    heliocentrics=integers(min_value=0, max_value=6),
    geocentrics=integers(min_value=0, max_value=5),
)
def test_journal_count_win(game, heliocentrics, geocentrics):
    """Test that a game instance concludes correctly when a team has reached its
    objective."""

    game.publications = {"H": heliocentrics, "G": geocentrics}
    result = game.journal_count_win()

    if result:
        if heliocentrics == 6:
            assert game.winner == "M"
            assert "maverick" in game.message
        elif geocentrics == 5:
            assert game.winner == "C"
            assert "conformist" in game.message
        else:
            assert False

    else:
        assert game.winner is None
        assert game.message is None


@given(game=games(), denounced=booleans())
def test_galileo_denounced_win(game, denounced):
    """Test that a game instance concludes with a conformist win if Galileo is
    denounced."""

    game.assign_roles()
    game.galileo.denounced = denounced
    result = game.galileo_denounced_win()

    if result:
        assert game.winner == "C"
        assert "conformist" in game.message

    else:
        assert game.winner is None
        assert game.message is None


@given(game=games())
def test_turn(game):
    """Test that a game instance can complete a full turn."""

    game.assign_roles()
    assert not game.turn()

    published = game.last_successfully_published

    if published is None:
        assert game.ex_dean is None
        assert game.ex_editor is None
        assert game.pressure_to_print == 1
        assert sum(game.publications.values()) == 0

    else:
        assert game.ex_dean is game.dean
        assert game.ex_editor is game.editor
        assert game.publications[published] == 1
        assert sum(game.publications.values()) == 1
        assert game.pressure_to_print == 0


@given(game=games())
def test_play(game):
    """Test that a game instance can complete an entire game."""

    try:
        winner, message = game.play()
    except RecursionError:
        assume(False)

    assert winner in ("C", "M")
    assert isinstance(message, str)

    if "rhetorical" in message:
        assert winner == "M"
        assert game.editor == game.galileo
        assert game.publications["H"] >= 3

    if "ousted" in message:
        assert winner == "C"
        assert game.galileo.denounced is True

    if "altered" in message:
        assert winner == "M"
        assert game.publications["H"] == 6
        assert game.publications["G"] < 5

    if "quelled" in message:
        assert winner == "C"
        assert game.publications["G"] == 5
        assert game.publications["H"] < 6
