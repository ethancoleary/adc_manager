import random
import json
from pathlib import Path

from otree.api import *
import pandas as pd
from common import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Survey1'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


def sample_sorted_r3scores(csv_name):
    csv_path = Path('_static') / csv_name
    df = pd.read_csv(csv_path)
    sampled = df.sample(n=10)
    scores = sampled['r3score'].sort_values().tolist()
    return scores


class Player(BasePlayer):
    gender1 = models.IntegerField()
    sob_gender1 = models.IntegerField()

    decision_bonus = models.IntegerField()
    bonus = models.FloatField(initial=0)

    m_50p = models.IntegerField(blank=True)
    m_25p = models.IntegerField(blank=True)
    m_75p = models.IntegerField(blank=True)
    m_array = models.LongStringField(blank=True)

    m_50p_sig = models.IntegerField(blank=True)
    m_25p_sig = models.IntegerField(blank=True)
    m_75p_sig = models.IntegerField(blank=True)
    m_array_signal = models.LongStringField(blank=True)

    f_50p = models.IntegerField(blank=True)
    f_25p = models.IntegerField(blank=True)
    f_75p = models.IntegerField(blank=True)
    f_array = models.LongStringField(blank=True)

    f_50p_sig = models.IntegerField(blank=True)
    f_25p_sig = models.IntegerField(blank=True)
    f_75p_sig = models.IntegerField(blank=True)
    f_array_signal = models.LongStringField(blank=True)

    n_50p = models.IntegerField(blank=True)
    n_25p = models.IntegerField(blank=True)
    n_75p = models.IntegerField(blank=True)
    n_array = models.LongStringField(blank=True)

    n_50p_sig = models.IntegerField(blank=True)
    n_25p_sig = models.IntegerField(blank=True)
    n_75p_sig = models.IntegerField(blank=True)
    n_array_signal = models.LongStringField(blank=True)

    sob = models.IntegerField(blank=True)

    blur_log = models.LongStringField(blank=True)
    blur_count = models.IntegerField(initial=0, blank=True)
    blur_warned = models.IntegerField(initial=0, blank=True)

    def m_array_list(self):
        return json.loads(self.m_array or '[]')

    def m_array_signal_list(self):
        return json.loads(self.m_array_signal or '[]')

    def f_array_list(self):
        return json.loads(self.f_array or '[]')

    def f_array_signal_list(self):
        return json.loads(self.f_array_signal or '[]')

    def n_array_list(self):
        return json.loads(self.n_array or '[]')

    def n_array_signal_list(self):
        return json.loads(self.n_array_signal or '[]')


# ---- Bonus helper -----------------------------------------------------------
# Exactly ONE "block" of survey decisions is paid, chosen at random via
# player.decision_bonus (set in Introduction). A block is three questions, so
# the maximum survey bonus is 3 x £0.30 = £0.90. Block numbering:
#   1 = distributions, first  gender block  (neutral distributions for treatment 1)
#   2 = signals,       first  gender block  (neutral signals       for treatment 1)
#   3 = second-order belief (SOB)           (paid post-hoc, no in-app accrual)
#   4 = distributions, second gender block  (treatment 2 only)
#   5 = signals,       second gender block  (treatment 2 only)
#
# A page only awards its £0.30 when its own block was the one drawn, so a
# participant can never be paid for both the distribution and the signal block.
def award_block_bonus(player, block, field_name, values, lo, hi):
    if player.decision_bonus == block:
        answer = player.field_maybe_none(field_name)
        if answer is not None and values[lo] <= answer <= values[hi]:
            player.bonus += 0.3
    # Keep the participant-level total in sync after every graded page so the
    # Results page always has a value regardless of which path was taken.
    player.participant.survey_bonus = player.bonus


class Introduction(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        MyBasePage.before_next_page(player, timeout_happened)

        player.gender1 = random.randint(1, 2)
        player.sob_gender1 = random.randint(1, 2)

        player.m_array = json.dumps(sample_sorted_r3scores('male_full.csv'))
        player.m_array_signal = json.dumps(sample_sorted_r3scores('male_signal.csv'))
        player.f_array = json.dumps(sample_sorted_r3scores('female_full.csv'))
        player.f_array_signal = json.dumps(sample_sorted_r3scores('female_signal.csv'))

        player.n_array = json.dumps(sample_sorted_r3scores('all_full.csv'))
        player.n_array_signal = json.dumps(sample_sorted_r3scores('all_signal.csv'))

        if player.participant.treatment == 1:
            player.decision_bonus = random.randint(1, 2)
        else:
            player.decision_bonus = random.randint(1, 5)

        player.participant.bonus_page = player.decision_bonus
        player.participant.survey_bonus = 0

### DISTRIBUTIONS 1  (block 1)

class distribution_males1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'm_50p', player.m_array_list(), 4, 5)

class distribution_males1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'm_75p', player.m_array_list(), 7, 8)

class distribution_males1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'm_25p', player.m_array_list(), 1, 2)

class distribution_females1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'f_50p', player.f_array_list(), 4, 5)

class distribution_females1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'f_75p', player.f_array_list(), 7, 8)

class distribution_females1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'f_25p', player.f_array_list(), 1, 2)

class distribution_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'n_50p', player.n_array_list(), 4, 5)

class distribution_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'n_75p', player.n_array_list(), 7, 8)

class distribution_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 1, 'n_25p', player.n_array_list(), 1, 2)

###############
### SIGNALS 1  (block 2)
###############
class signal_males1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'm_50p_sig', player.m_array_signal_list(), 4, 5)

class signal_males1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'm_75p_sig', player.m_array_signal_list(), 7, 8)


class signal_males1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'm_25p_sig', player.m_array_signal_list(), 1, 2)

class signal_females1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'f_50p_sig', player.f_array_signal_list(), 4, 5)


class signal_females1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'f_75p_sig', player.f_array_signal_list(), 7, 8)


class signal_females1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'f_25p_sig', player.f_array_signal_list(), 1, 2)


class signal_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'n_50p_sig', player.n_array_signal_list(), 4, 5)


class signal_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'n_75p_sig', player.n_array_signal_list(), 7, 8)


class signal_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 2, 'n_25p_sig', player.n_array_signal_list(), 1, 2)


###################
### SOB  (block 3 - paid post-hoc, no in-app accrual)
###################
class SOB(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['sob']

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        player.participant.survey_bonus = player.bonus

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.sob_gender1 == 1

class SOB2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['sob']

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        player.participant.survey_bonus = player.bonus

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.sob_gender1 == 2

###################
### DISTRIBUTIONS 2  (block 4)
###################

class distribution_males2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'm_50p', player.m_array_list(), 4, 5)

class distribution_males2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'm_75p', player.m_array_list(), 7, 8)

class distribution_males2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'm_25p', player.m_array_list(), 1, 2)

class distribution_females2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'f_50p', player.f_array_list(), 4, 5)

class distribution_females2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'f_75p', player.f_array_list(), 7, 8)

class distribution_females2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 4, 'f_25p', player.f_array_list(), 1, 2)

###############
### SIGNALS 2  (block 5)
###############
class signal_males2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'm_50p_sig', player.m_array_signal_list(), 4, 5)

class signal_males2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'm_75p_sig', player.m_array_signal_list(), 7, 8)


class signal_males2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'm_25p_sig', player.m_array_signal_list(), 1, 2)

class signal_females2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'f_50p_sig', player.f_array_signal_list(), 4, 5)


class signal_females2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'f_75p_sig', player.f_array_signal_list(), 7, 8)


class signal_females2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        award_block_bonus(player, 5, 'f_25p_sig', player.f_array_signal_list(), 1, 2)


page_sequence = [Introduction,

                 distribution_males1_q1,
                distribution_males1_q2,
                distribution_males1_q3,
                 distribution_females1_q1,
                distribution_females1_q2,
                distribution_females1_q3,
                distribution_q1,
                distribution_q2,
                distribution_q3,

                 signal_males1_q1,
                 signal_males1_q2,
                 signal_males1_q3,
                 signal_females1_q1,
                 signal_females1_q2,
                 signal_females1_q3,
                 signal_q1,
                 signal_q2,
                 signal_q3,

                SOB,
                 SOB2,

                distribution_males2_q1,
                distribution_males2_q2,
                distribution_males2_q3,
                 distribution_females2_q1,
                distribution_females2_q2,
                distribution_females2_q3,

                signal_males2_q1,
                 signal_males2_q2,
                 signal_males2_q3,
                 signal_females2_q1,
                 signal_females2_q2,
                 signal_females2_q3,

                 ]
