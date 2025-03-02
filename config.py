import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'mysql+pymysql://root:HamidMySql28@localhost/ht_booking'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False