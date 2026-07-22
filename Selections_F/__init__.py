from otree.api import *
import random
import time
from common import *
import pandas as pd

doc = '''
This is the main survey app. It contains
'''
def draw_quartet_id_array():
    path = "_static/quartets_python_binned.csv"  # adjust path if needed
    quartets = pd.read_csv(path)

    ids = quartets["quartet_id"].drop_duplicates().tolist()
    ids = [int(i) for i in ids if int(i) != 1200]

    if len(ids) < 20:
        raise ValueError(f"Need at least 20 quartet_ids excluding 1200, found {len(ids)}.")

    chosen_ids = random.sample(ids, 20)
    chosen_ids.append(1200)
    random.shuffle(chosen_ids)

    return chosen_ids


class C(CommonConstants):
    NAME_IN_URL = 'Main_part'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    PIECE_RATE = 0.05

    Round_length = 120
    Min_round_length = Round_length
    Timer_text = "Time left to complete this round:"

    Calculator_path = "_templates/global/Calculator.html"

    Instructions_choice_path = "_templates/global/Instructions_choice.html"
    Instructions_choice_past_path = "_templates/global/Instructions_choice_past.html"
    Instructions_choice_2_path = "_templates/global/Instructions_choice_2.html"

    MathMemory_pic = 'https://raw.githubusercontent.com/argunaman2022/stereotypes-replication2/master/_static/pics/MathMemory_pic.png'

    Belief_Treatment_male = "_templates/global/Belief_treatment_male.html"
    Belief_Treatment_female = "_templates/global/Belief_treatment_female.html"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    page_pass_time = models.FloatField()

    incentivised_selection = models.IntegerField()

    CQ1 = models.IntegerField(blank=True)
    CQ1_wrong = models.IntegerField(initial=0)
    CQ2 = models.IntegerField(blank=True)
    CQ2_wrong = models.IntegerField(initial=0)
    CQ3 = models.IntegerField(blank=True)
    CQ3_wrong = models.IntegerField(initial=0)

    cq_stage = models.IntegerField(initial=1)

    Comprehension_password = models.StringField(blank=False, label='Password')

    clicked_info = models.StringField(initial=False)
    Calculator = models.StringField(min=0, max=100, blank=True, label='Calculator')

    blur_log = models.LongStringField(blank=True)
    blur_count = models.IntegerField(initial=0, blank=True)
    blur_warned = models.IntegerField(initial=0, blank=True)


# ==== Helper functions for selections ====

def get_row(player: Player, which_line: int):
    rows = get_rows_for_treatment(player.treatment)
    if rows is None:
        return None
    index = getattr(player, f'SelectionLine{which_line}')
    return rows[index]


def vars_for_selection(player: Player, which_line: int):
    row = get_row(player, which_line)
    if row is None:
        return dict(
            score1=None, score2=None, score3=None, score4=None,
            gender1=None, gender2=None, gender3=None, gender4=None
        )
    return dict(
        score1=row['round2'][0],
        score2=row['round2'][1],
        score3=row['round2'][2],
        score4=row['round2'][3],
        gender1=row['gender'][0],
        gender2=row['gender'][1],
        gender3=row['gender'][2],
        gender4=row['gender'][3],
    )


def process_selection(player: Player, which_line: int, choice_field: str, id_field: str):
    row = get_row(player, which_line)
    if row is None:
        return

    choice = getattr(player, choice_field)

    # record chosen id
    if choice in [1, 2, 3, 4]:
        chosen_id = row['ids'][choice - 1]
        setattr(player, id_field, str(chosen_id))

    # record groupid for this selection
    setattr(player, f'Selection{which_line}_group', row['groupid'])

    # bonus logic (highest round3score)
    round3 = row['round3']
    max_idx = max(range(4), key=lambda i: round3[i]) + 1
    if player.incentivised_selection == which_line and choice == max_idx:
        player.bonus = 1

# ==== Pages ====

class Selection_instructions(MyBasePage):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        MyBasePage.before_next_page(player, timeout_happened)
        player.page_pass_time = time.time() + C.Min_round_length

        player.incentivised_selection = random.randint(1, 5)
        player.participant.incentivised_selection = player.incentivised_selection

        quartet_ids = draw_quartet_id_array()
        player.participant.quartet_ids = quartet_ids


class Comprehension_Qs(MyBasePage):
    extra_fields = ['CQ1', 'CQ2', 'CQ3', 'cq_stage']
    form_fields = MyBasePage.form_fields + extra_fields

    @staticmethod
    def is_displayed(player: Player):
        return player.cq_stage in [1, 2, 3]

    @staticmethod
    def vars_for_template(player: Player):
        context = MyBasePage.vars_for_template(player)
        context.update(cq_stage=player.cq_stage)
        return context

    @staticmethod
    def error_message(player: Player, values):
        stage = int(values.get('cq_stage') or 1)
        pv = player.participant.vars

        if stage == 1:
            if values.get('CQ1') != 3:
                pv['CQ1_wrong_temp'] = pv.get('CQ1_wrong_temp', 0) + 1
                return {'CQ1': 'That is not correct. Please try again.'}

        elif stage == 2:
            if values.get('CQ2') != 2:
                pv['CQ2_wrong_temp'] = pv.get('CQ2_wrong_temp', 0) + 1
                return {'CQ2': 'That is not correct. Please try again.'}

        elif stage == 3:
            if values.get('CQ3') != 1:
                pv['CQ3_wrong_temp'] = pv.get('CQ3_wrong_temp', 0) + 1
                return {'CQ3': 'That is not correct. Please try again.'}

    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        MyBasePage.before_next_page(player, timeout_happened)

        pv = player.participant.vars
        player.CQ1_wrong = pv.get('CQ1_wrong_temp', 0)
        player.CQ2_wrong = pv.get('CQ2_wrong_temp', 0)
        player.CQ3_wrong = pv.get('CQ3_wrong_temp', 0)

        if player.cq_stage < 3:
            player.cq_stage += 1




class SelectionsBegin(MyBasePage):
    pass


page_sequence = [
    Selection_instructions,
    Comprehension_Qs,
    Comprehension_Qs,
    Comprehension_Qs,
    SelectionsBegin,

]
