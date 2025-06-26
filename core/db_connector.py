import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv(dotenv_path="config/settings.env")

def get_engine():
    return create_engine(os.getenv("DB_CONNECTION_STRING"))
