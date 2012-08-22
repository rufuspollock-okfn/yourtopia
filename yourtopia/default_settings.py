import os
__HERE__ = os.path.dirname(os.path.abspath(__file__))

DEBUG = False

# webserver host and port
HOST = '0.0.0.0'
PORT = 5000

SECRET = 'foobar'
SECRET_KEY = 'my-session-secret'

I18N_STRINGS_PATH = os.path.join(__HERE__, 'static/data/i18n.csv')
# path to the metadata JSON file
METADATA_PATH = os.path.join(__HERE__, 'static/data/metadata.json')
# Path to SQLite DB file
DATABASE = os.path.join(__HERE__, 'static/data/database.db')

# Database URI for SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(__HERE__, 'static/data/database.db')

THUMBS_PATH = os.path.join(__HERE__, 'static/thumbs')

# languages available, sorted by priority
LANG_PRIORITIES = ['it', 'en']

# Number of elements per page on the Browse All page
BROWSE_PERPAGE = 9
