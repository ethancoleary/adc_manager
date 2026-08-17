from otree.api import *
from common import CommonConstants


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
    @staticmethod
    def vars_for_template(player: Player):
        p = player.participant

        completion_fee = CommonConstants.Completion_fee
        hiring_bonus = 1.00 if p.main_bonus == 1 else 0.00
        # bonus_page == 3 is the second-order-belief block, scored post-hoc.
        survey_pending = p.bonus_page == 3
        survey_bonus = p.survey_bonus

        rows = [
            dict(source='Completion payment', amount=f"£{completion_fee:.2f}"),
            dict(source='Hiring decision', amount=f"£{hiring_bonus:.2f}"),
        ]

        settled_total = completion_fee + hiring_bonus
        if survey_pending:
            rows.append(dict(source='Survey questions', amount='To be determined*'))
            # Survey amount unknown, so the total is the settled part plus a marker.
            total_display = f"£{settled_total:.2f} + survey bonus*"
        else:
            rows.append(dict(source='Survey questions', amount=f"£{survey_bonus:.2f}"))
            total_display = f"£{settled_total + survey_bonus:.2f}"

        return {
            # Format once here to avoid fragile float-equality in the template
            # (e.g. 0.3 + 0.3 + 0.3 == 0.9 is False in floating point).
            'survey_bonus_display': f"{survey_bonus:.2f}",
            'bonus_rows': rows,
            'bonus_total_display': total_display,
            'survey_pending': survey_pending,
        }

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
