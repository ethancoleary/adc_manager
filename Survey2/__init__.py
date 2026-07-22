from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Survey2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    country = models.IntegerField(
        choices=[[1, 'UK'],
                 [2, 'USA'],
                 [3, 'Other']]
    )

    education_uk = models.IntegerField(
    )
    ethnicity_uk = models.IntegerField(blank=True)
    political_uk = models.IntegerField(blank=True)

    education_us = models.IntegerField(blank=True)
    ethnicity_us = models.IntegerField(blank=True)
    political_us = models.IntegerField(blank=True)

    Risk = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        widget=widgets.RadioSelectHorizontal,
        label="Please select your risk level (0–10):"
    )

    manager_exp = models.IntegerField(blank=True)
    past_discrim = models.IntegerField(blank=True)

    blur_log = models.LongStringField(blank=True)
    blur_count = models.IntegerField(initial=0, blank=True)
    blur_warned = models.IntegerField(initial=0, blank=True)


# PAGES
class Country(Page):
    form_model = 'player'
    form_fields = ['country',
                   'blur_log',
                   'blur_count',
                   'blur_warned']

    @staticmethod
    def vars_for_template(player: Player):

        return {
            'hidden_fields': ['blur_log', 'blur_count','blur_warned', 'browser'],
        }


class Socioeconomics_UK(Page):
    form_model = 'player'
    form_fields = ['education_uk',
                   'ethnicity_uk',
                   'political_uk',
                   'blur_log',
                   'blur_count',
                   'blur_warned']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'hidden_fields': ['blur_log', 'blur_count', 'blur_warned', 'browser'],
        }

    @staticmethod
    def is_displayed(player: Player):
        return player.country==1

class Socioeconomics_US(Page):
    form_model = 'player'
    form_fields = ['education_us',
                   'ethnicity_us',
                   'political_us',
                   'blur_log',
                   'blur_count',
                   'blur_warned']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'hidden_fields': ['blur_log', 'blur_count', 'blur_warned', 'browser'],
        }

    @staticmethod
    def is_displayed(player: Player):
        return player.country > 1


class Experience(Page):
    form_model = 'player'
    form_fields = ['Risk',
                   'manager_exp',
                   'past_discrim',
                   'blur_log',
                   'blur_count',
                   'blur_warned']

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'hidden_fields': ['blur_log', 'blur_count', 'blur_warned', 'browser'],
        }

class Results(Page):
    pass

class Redirect(Page):

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.subsession.session.config['completionlink']
        )



page_sequence = [
    Country,
    Socioeconomics_UK,
    Socioeconomics_US,
    Experience,
    Results,
    Redirect
]
