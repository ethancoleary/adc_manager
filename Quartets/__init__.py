from otree.api import *
import pandas as pd
from common import *

doc = """
21-round worker selection app.
"""


class C(CommonConstants):
    NAME_IN_URL = 'Quartets'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 21


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    Selection = models.IntegerField(choices=[1, 2, 3, 4])

    quartet_id = models.IntegerField()

    w1_female = models.IntegerField()
    w1_r2score = models.IntegerField()
    w1_r3score = models.IntegerField()
    w1_participantlabel = models.StringField()

    w2_female = models.IntegerField()
    w2_r2score = models.IntegerField()
    w2_r3score = models.IntegerField()
    w2_participantlabel = models.StringField()

    w3_female = models.IntegerField()
    w3_r2score = models.IntegerField()
    w3_r3score = models.IntegerField()
    w3_participantlabel = models.StringField()

    w4_female = models.IntegerField()
    w4_r2score = models.IntegerField()
    w4_r3score = models.IntegerField()
    w4_participantlabel = models.StringField()

    top_r3score = models.IntegerField()
    selected_worker_female = models.IntegerField(blank=True)
    selected_worker_r2score = models.IntegerField(blank=True)
    selected_worker_r3score = models.IntegerField(blank=True)
    bonus = models.IntegerField(initial=0)

    blur_log = models.LongStringField(blank=True)
    blur_count = models.IntegerField(initial=0, blank=True)
    blur_warned = models.IntegerField(initial=0, blank=True)


def get_quartet_df():
    return pd.read_csv("_static/quartets_python_binned.csv")


def get_round_workers(player: Player):
    quartet_ids = player.participant.vars.get('quartet_ids')
    if not quartet_ids:
        raise ValueError("participant.vars['quartet_ids'] is missing.")

    current_qid = quartet_ids[player.round_number - 1]
    df = get_quartet_df()

    rows = df[df['quartet_id'] == current_qid].copy()

    if len(rows) != 4:
        raise ValueError(
            f"quartet_id {current_qid} in round {player.round_number} has {len(rows)} rows, expected 4."
        )

    return current_qid, rows


def assign_round_workers(player: Player):
    pv = player.participant.vars
    key = f'quartet_order_round_{player.round_number}'

    if key not in pv:
        current_qid, rows = get_round_workers(player)
        rows = rows.sample(frac=1).reset_index(drop=True)

        pv[key] = {
            'quartet_id': int(current_qid),
            'workers': rows.to_dict('records'),
        }

    assigned = pv[key]
    player.quartet_id = assigned['quartet_id']

    for i, row in enumerate(assigned['workers'], start=1):
        setattr(player, f'w{i}_participantlabel', str(row['participantlabel']))
        setattr(player, f'w{i}_female', int(row['female']))
        setattr(player, f'w{i}_r2score', int(row['r2score']))
        setattr(player, f'w{i}_r3score', int(row['r3score']))


class SelectionPage(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['Selection']

    @staticmethod
    def vars_for_template(player: Player):
        context = MyBasePage.vars_for_template(player)

        assign_round_workers(player)

        context.update(
            round_no=player.round_number,
            quartet_id=player.quartet_id,
            score1=player.w1_r2score,
            score2=player.w2_r2score,
            score3=player.w3_r2score,
            score4=player.w4_r2score,
            gender1=2 if player.w1_female == 1 else 1,
            gender2=2 if player.w2_female == 1 else 1,
            gender3=2 if player.w3_female == 1 else 1,
            gender4=2 if player.w4_female == 1 else 1,
        )
        return context

    @staticmethod
    def before_next_page(player: Player, timeout_happened=False):
        MyBasePage.before_next_page(player, timeout_happened)

        assign_round_workers(player)

        player.top_r3score = max(
            player.w1_r3score,
            player.w2_r3score,
            player.w3_r3score,
            player.w4_r3score,
        )

        choice = player.Selection
        selected_r3score = getattr(player, f'w{choice}_r3score')

        player.selected_worker_female = getattr(player, f'w{choice}_female')
        player.selected_worker_r2score = getattr(player, f'w{choice}_r2score')
        player.selected_worker_r3score = selected_r3score

        if player.participant.vars.get('incentivised_selection') == player.round_number:
            if selected_r3score == player.top_r3score:
                player.bonus = 1
                player.participant.main_bonus = 1
            else:
                player.bonus = 0
                player.participant.main_bonus = 0


class SelectionPage_A(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['Selection']

    @staticmethod
    def vars_for_template(player: Player):
        context = MyBasePage.vars_for_template(player)
        context.update(
            round_no=player.round_number,
            gender1=1,  # male
            gender2=2,  # female
            gender3=2,  # female
            gender4=1,  # male
            score1='a',
            score2='b',
            score3='c',
            score4='d',
        )
        return context

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 5

class SelectionPage_B(MyBasePage):
    form_model = 'player'
    form_fields = MyBasePage.form_fields + ['Selection']

    @staticmethod
    def vars_for_template(player: Player):
        context = MyBasePage.vars_for_template(player)
        context.update(
            round_no=player.round_number,
            gender1=2,  # male
            gender2=1,  # female
            gender3=2,  # female
            gender4=1,  # male
            score1='a',
            score2='b',
            score3='c',
            score4='d',
        )
        return context

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 16



class MidPage(MyBasePage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 10


page_sequence = [
    SelectionPage,
    SelectionPage_A,
    SelectionPage_B,
    MidPage]