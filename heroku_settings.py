import os

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                            os.environ.get('SHARED_DATABASE_URL'))

