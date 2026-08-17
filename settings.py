from os import environ

DEBUG = False

SESSION_CONFIGS = [
    dict(name='test',

         app_sequence=[
             'Intro_Round1',
             'Selections_F',
             'Quartets',
             'Survey1',
            'Survey2'
         ],

         num_demo_participants=2,

         completionlink=
         'https://app.prolific.com/submissions/complete?cc=C11YBC1V',

         # TODO: replace with the dedicated Prolific screen-out completion code
         # before launch. Placeholder for now so RedirectScreenOut does not crash.
         completionlinkscreenout=
         'https://app.prolific.com/submissions/complete?cc=SCREENOUT_CODE_TODO',

         # Flagged bots are sent to the Prolific homepage to return manually.
         completionlinkbot=
         'https://app.prolific.com/',

         )


]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

ROOMS = [
    dict( name = 'Study', display_name = 'Study'),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="", use_browser_bots=False,
)


PARTICIPANT_FIELDS = [
     'Promised',
    'Comprehension_passed', 'treatment',
    'Attention_passed', 'Attention_1', 'Attention_2', 'Attention_3',
        'Gender', 'Choice',
    'Blur_count', 'Blur_log', 'Blur_warned', 'R1_score', 'R2_score', 'R3_score',
    'round_for_payment', 'page_for_payment', 'R2_mix', 'incentivised_selection', 'main_bonus',
    'quartet_ids', 'survey_bonus', 'bonus_page'

]



# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = 'ADMIN_PASSWORD_APPLY'

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'SECRET_KEY_APPLY'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'otree_db',           # The name of your PostgreSQL database
        'USER': 'otree_user',          # The username you created
        'PASSWORD': 'DB_PASSWORD_APPLY',   # The password for the user
        'HOST': 'localhost',           # Localhost for local testing
        'PORT': '5432',                # Default PostgreSQL port
    }
}