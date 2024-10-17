from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import logging

logging.basicConfig(level=logging.INFO)

class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

try:
    config = Settings()
    logging.info("Configuration successfully loaded.")
except Exception as e:
    logging.error(f"Error loading configuration: {e}")
    raise


