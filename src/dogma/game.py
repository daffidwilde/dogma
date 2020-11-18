"""The essential classes and functions to run a game instance."""

import random


class DogmaGame:
    """A class to represent and manage the components of a game."""

    def __init__(self, players, seed=None):

        if isinstance(seed, int):
            random.seed(seed)

        self.players = players
        self.seed = seed
        self.winner = None
        self.message = None

        cards = ["H"] * 11 + ["G"] * 6
        random.shuffle(cards)
        self.journal_cards = cards
        self.discard_pile = []

        self.publications = {"H": 0, "G": 0}
        self.last_successfully_published = None
        self.pressure_to_print = 0
        self.overrule_available = False

        self.galileo = None
        self.maverick = None
        self.dean = None
        self.editor = None
        self.ex_dean = None
        self.ex_editor = None

    def shuffle_roles(self):
        """Shuffle the available roles."""

        roles = ["C"] * (len(self.players) - 2) + ["M", "G"]
        random.shuffle(roles)

        return roles

    def assign_roles(self):
        """Assign the roles to the players."""

        roles = self.shuffle_roles()
        for player, role in zip(self.players, roles):
            player.role = role

            if role == "G":
                self.galileo = player
            if role == "M":
                self.maverick = player

    def inform_mavericks(self):
        """Reveal the identities of galileo and the maverick to one another."""

        self.maverick.partner = self.galileo
        self.galileo.partner = self.maverick

    def elect_first_dean(self):
        """Select the first dean. This is done automatically (for now)."""

        self.dean = random.choice(self.players)

    def set_next_dean(self):
        """Set the dean to be the next player in a clockwise fashion. If that
        player has been denounced, move on."""

        idx = (self.players.index(self.dean) + 1) % len(self.players)
        self.dean = self.players[idx]
        if self.dean.denounced:
            self.set_next_dean()

    def _get_players_for_nomination(self):
        """Get the players that can be nominated."""

        if len(self.players) == 5:
            return tuple(
                p
                for p in self.players
                if p not in (self.dean, self.ex_editor) and not p.denounced
            )

        return tuple(
            p
            for p in self.players
            if p not in (self.dean, self.ex_dean, self.ex_editor)
            and not p.denounced
        )

    def form_print_team(self):
        """Get a nomination from the dean for an editor."""

        nomination = self.dean.nominate(self._get_players_for_nomination())

        return nomination

    def cast_vote(self, nomination):
        """Cast a vote on the suggested print team."""

        votes = {"yes": 0, "no": 0}
        for player in self.players:
            if not player.denounced:
                votes[player.vote(nomination)] += 1

        ayes, nays = votes.values()
        self.pressure_to_print += 1 * (ayes <= nays)
        return ayes > nays

    def draw_journals(self, num=3):
        """Draw a number of journal cards from the top of the deck (three by
        default). If there are not enough cards left, shuffle the remaining
        cards with the discard pile and draw again."""

        if len(self.journal_cards) >= num:
            drawn = self.journal_cards[:num]
            self.journal_cards = self.journal_cards[num:]
            return drawn

        cards = self.journal_cards + self.discard_pile
        random.shuffle(cards)

        self.journal_cards = cards
        self.discard_pile = []

        return self.draw_journals()

    def form_publication(self):
        """With the dean and editor decided, form a publication from three
        journal cards. If the overrule power is unlocked then"""

        choices, reject, _ = self.dean.choose_cards_to_submit(
            self.draw_journals()
        )
        self.discard_pile.append(reject)

        kept, reject, suggest_overrule = self.editor.choose_cards_to_submit(
            choices, self.overrule_available
        )

        if suggest_overrule:
            deans_decision = self.dean.agree_to_overrule()
            if deans_decision:
                self.pressure_to_print += 1
                return False

            kept, reject, _ = self.editor.choose_cards_to_submit(
                choices + [reject]
            )

        self.discard_pile.append(reject)
        choice = kept[0]

        self.publications[choice] += 1
        self.last_successfully_published = choice
        self.pressure_to_print = 0
        self.ex_dean = self.dean
        self.ex_editor = self.editor

        return True

    def emergency_publication(self):
        """The pressure to print has forced the society to print whatever is at
        the top of the deck."""

        choice = self.draw_journals(1)[0]

        self.publications[choice] += 1
        self.last_successfully_published = None
        self.pressure_to_print = 0

    def _get_players_for_denouncement(self):
        """Get the players that can be denounced."""

        return tuple(
            p for p in self.players if p is not self.dean and not p.denounced
        )

    def perform_emergency_actions(self):
        """As things become more desperate for the conformists, special powers
        are given to the sitting print team:

            - After the third maverick publication, the sitting dean can look at
              the next three journal cards to be drawn.
            - After the fourth and fifth maverick publications, the dean can
              remove any player from the game by denouncing them. If Galileo is
              denounced, the game is over.
            - After the fifth maverick publication, the print team has the
              ability to opt out of publishing a journal by agreeing to throw
              out their hand. The editor instigates and if the dean does not
              agree then a publication must follow as normal.
        """

        if self.publications["H"] == 3:
            cards = self.draw_journals()
            self.journal_cards = cards + self.journal_cards
            self.dean.seen = cards

        if self.publications["H"] in [4, 5]:
            player = self.dean.denounce(self._get_players_for_denouncement())
            player.denounced = True
            if self.galileo_denounced_win():
                return True

        if self.publications["H"] == 5:
            self.overrule_available = True

        return False

    def galileo_editor_win(self):
        """Check if the mavericks win by installing Galileo as editor with at
        least three favourable journals published."""

        if self.editor.role == "G" and self.publications["H"] >= 3:
            self.winner = "M"
            self.message = "Galileo's rhetorical prowess has dominated."
            return True

        return False

    def journal_count_win(self):
        """Check if either team has filled its journal slots."""

        if self.publications["H"] == 6:
            self.winner = "M"
            self.message = "The maverick thinkers have altered the status quo."
            return True

        if self.publications["G"] == 5:
            self.winner = "C"
            self.message = "The conformists have quelled the free-thinkers."
            return True

        return False

    def galileo_denounced_win(self):
        """Check if Galileo has been denounced."""

        if self.galileo.denounced:
            self.winner = "C"
            self.message = "The conformists have successfully ousted Galileo."
            return True

        return False

    def turn(self):
        """Play a complete turn of the game."""

        if self.dean is None:
            self.elect_first_dean()
        else:
            self.set_next_dean()

        nomination = self.form_print_team()
        successful = self.cast_vote(nomination)

        if successful:
            self.editor = nomination
            if self.galileo_editor_win():
                return True

            if not self.form_publication():
                self.pressure_to_print += 1
                return False

        if self.pressure_to_print == 3:
            self.emergency_publication()

        if self.journal_count_win():
            return True

        if successful and self.last_successfully_published == "H":
            self.perform_emergency_actions()

        if self.galileo_denounced_win():
            return True

        return False

    def play(self):
        """Play a game of looping turns until one team wins."""

        self.assign_roles()
        self.inform_mavericks()

        no_winner = True
        while no_winner:
            no_winner = not self.turn()

        return self.winner, self.message
