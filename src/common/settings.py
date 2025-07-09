from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    def __init__(self):
        super().__init__()
        load_dotenv()
