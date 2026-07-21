# common.py

from otree.api import Page
from otree.api import BaseConstants
from otree.api import  models, widgets
import json




    



# %% Constants
class CommonConstants(BaseConstants):
    Completion_fee = 3.50
    Max_Bonus = 10  


    
    # Prolific links:
    Completion_redirect = "https://www.wikipedia.org/" #TODO: adjust completion redirect
    Reject_redirect = "https://www.wikipedia.org/" #TODO: adjust reject redirect
    Return_redirect = "https://www.wikipedia.org/" #TODO: adjust return redirect
    
    Instructions_Manager_MM_path = "_templates/global/Instructions_Manager_MM.html"
    Instructions_Manager_ER_path = "_templates/global/Instructions_Manager_ER.html"
    Selection_Instructions = "_templates/global/Selection_instructions_template.html"

    Task_instructions_path = "_templates/global/Task_instructions.html"
    Task_instructions_MM_path = "_templates/global/Task_instructions_MM.html"
    Task_instructions_ER_path = "_templates/global/Task_instructions_ER.html"


# %% Player
# DOESNT WORK WITH PLAYER

# %% Pages
class MyBasePage(Page):
    form_model = 'player'
    form_fields = ['blur_log', 'blur_count', 'blur_warned']


    @staticmethod
    def vars_for_template(player):
 # --- Instructions path logic (updated) ---
        # Use neutral instructions if treatment hides gender (1 or 9).





       # if player.participant.Gender == '':
        #    Instructions_path = CommonConstants.Instructions_female_path
        #elif player.participant.Gender == 'Male':
         #       Instructions_path = CommonConstants.Instructions_male_path
        #else: Instructions_path = CommonConstants.Instructions_female_path


        Task_path = CommonConstants.Task_instructions_MM_path
        Instructions_path = CommonConstants.Instructions_Manager_MM_path


        if player.participant.vars.get('Blur_warned', 0) == 1:
            player.blur_warned = 1

        if player.participant.treatment < 9:
            task = "Maths-Memory"
        else:
            task = "Emotion Recognition"
            

        return {
            'hidden_fields': ['blur_log', 'blur_count','blur_warned'],
            'Completion_fee': CommonConstants.Completion_fee,
            
            'Instructions_path': Instructions_path,
            'Task_path': Task_path,
            'Task_instructions': Task_path,
            'Selection_instructions': CommonConstants.Selection_Instructions,
            'task': task,
        }
        
        
                   

    @staticmethod
    def before_next_page(player, timeout_happened=False):
        blob = player.blur_log or '{}'
        page_counts = json.loads(blob)
        Blur_log = player.participant.vars.get('Blur_log', {})
        for page_name, count in page_counts.items():
            Blur_log[page_name] = Blur_log.get(page_name, 0) + count
        player.participant.vars['Blur_log'] = Blur_log
        blur_count = player.field_maybe_none('blur_count') or 0

        player.participant.vars['Blur_count'] = (
                player.participant.vars.get('Blur_count', 0) + blur_count
        )
        
        # if player has been warned in this page, we set the flag and keep track of it, if not we keep the previous value
        # TODO: decide if you want the bonus to be determined based on the blur_warned flag, if so, adjust your bonus logic accordingly
        blur_warned = player.field_maybe_none('blur_warned') or 0

        if blur_warned == 1:
            player.participant.vars['Blur_warned'] = 1
        
