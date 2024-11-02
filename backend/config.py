import os

class Config:
    SECRET_KEY = os.getenv('movers', 'your_production_secret_key')
    DEBUG = False  # Disable debug mode
    TESTING = False  # Disable testing mode

    # Database configurations (MySQL)
    DB_HOST = 'localhost'
    DB_USER = 'pinchez420'
    DB_PASSWORD = 'Rasbazu254.'
    DB_NAME = 'movers_transport_system'
