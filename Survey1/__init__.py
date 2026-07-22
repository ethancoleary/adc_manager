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
            player.decision_bonus = random.randint(1,2)
        else:
            player.decision_bonus = random.randint(1, 5)

        player.participant.bonus_page = player.decision_bonus

### DISTRIBUTIONS 1

class distribution_males1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.m_50p is not None and lower <= player.m_50p <= upper:
                player.bonus += 0.3

class distribution_males1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.m_75p is not None and lower <= player.m_75p <= upper:
                player.bonus += 0.3

class distribution_males1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.m_25p is not None and lower <= player.m_25p <= upper:
                player.bonus += 0.3

class distribution_females1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.f_50p is not None and lower <= player.f_50p <= upper:
                player.bonus += 0.3

class distribution_females1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.f_25p is not None and lower <= player.f_25p <= upper:
                player.bonus += 0.3

class distribution_females1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.f_75p is not None and lower <= player.f_75p <= upper:
                player.bonus += 0.3

class distribution_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.n_50p is not None and lower <= player.n_50p <= upper:
                player.bonus += 0.3

class distribution_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.n_75p is not None and lower <= player.n_75p <= upper:
                player.bonus += 0.3

class distribution_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.n_25p is not None and lower <= player.n_25p <= upper:
                player.bonus += 0.3

###############
### SIGNALS 1
###############
class signal_males1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.m_50p_sig is not None and lower <= player.m_50p_sig <= upper:
                player.bonus += 0.3

class signal_males1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.m_75p_sig is not None and lower <= player.m_75p_sig <= upper:
                player.bonus += 0.3


class signal_males1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.m_25p_sig is not None and lower <= player.m_25p_sig <= upper:
                player.bonus += 0.3

class signal_females1_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.f_50p_sig is not None and lower <= player.f_50p_sig <= upper:
                player.bonus += 0.3


class signal_females1_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.f_75p_sig is not None and lower <= player.f_75p_sig <= upper:
                player.bonus += 0.3


class signal_females1_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.f_25p_sig is not None and lower <= player.f_25p_sig <= upper:
                player.bonus += 0.3


class signal_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_signal_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.n_50p_sig is not None and lower <= player.n_50p_sig <= upper:
                player.bonus += 0.3


class signal_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_signal_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.n_75p_sig is not None and lower <= player.n_75p_sig <= upper:
                player.bonus += 0.3


class signal_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['n_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.n_array_signal_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.n_25p_sig is not None and lower <= player.n_25p_sig <= upper:
                player.bonus += 0.3


###################
### SOB
###################
class SOB(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['sob']

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        player.participant.survey_bonus = player.bonus

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.sob_gender1==1

class SOB2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['sob']

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        player.participant.survey_bonus = player.bonus

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.sob_gender1==2

###################
### DISTRIBUTIONS 1
###################

class distribution_males2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.m_50p is not None and lower <= player.m_50p <= upper:
                player.bonus += 0.3

class distribution_males2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.m_75p is not None and lower <= player.m_75p <= upper:
                player.bonus += 0.3

class distribution_males2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.m_25p is not None and lower <= player.m_25p <= upper:
                player.bonus += 0.3

class distribution_females2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.f_50p is not None and lower <= player.f_50p <= upper:
                player.bonus += 0.3

class distribution_females2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.f_75p is not None and lower <= player.f_75p <= upper:
                player.bonus += 0.3

class distribution_females2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.f_25p is not None and lower <= player.f_25p <= upper:
                player.bonus += 0.3

###############
### SIGNALS 1
###############
class signal_males2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.m_50p_sig is not None and lower <= player.m_50p_sig <= upper:
                player.bonus += 0.3

class signal_males2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.m_75p_sig is not None and lower <= player.m_75p_sig <= upper:
                player.bonus += 0.3


class signal_males2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['m_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 2

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.m_array_signal_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.m_25p_sig is not None and lower <= player.m_25p_sig <= upper:
                player.bonus += 0.3

        player.participant.survey_bonus = player.bonus

class signal_females2_q1(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_50p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[4]
        upper = arr[5]

        if player.decision_bonus == 1:
            if player.f_50p_sig is not None and lower <= player.f_50p_sig <= upper:
                player.bonus += 0.3


class signal_females2_q2(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_75p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[7]
        upper = arr[8]

        if player.decision_bonus == 1:
            if player.f_75p_sig is not None and lower <= player.f_75p_sig <= upper:
                player.bonus += 0.3


class signal_females2_q3(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['f_25p_sig']

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.treatment == 2 and player.gender1 == 1

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        arr = player.f_array_signal_list()
        lower = arr[1]
        upper = arr[2]

        if player.decision_bonus == 1:
            if player.f_25p_sig is not None and lower <= player.f_25p_sig <= upper:
                player.bonus += 0.3

        player.participant.survey_bonus = player.bonus


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