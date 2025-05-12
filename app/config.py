import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    DATABASE = os.path.join(BASE_DIR, 'data', 'mockserver.db')
    TESTING = False

class TestConfig(Config):
    DATABASE = os.path.join(BASE_DIR, 'data', 'test_mockserver.db')
    TESTING = True