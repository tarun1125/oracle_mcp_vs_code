import os
from dotenv import load_dotenv

def load_env(env_name: str):
    env_file = f".env.{env_name.lower()}"
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Environment file not found: {env_file}")
    load_dotenv(env_file)
    return {
        "ENV_NAME": os.getenv("ENV_NAME"),
        "ORACLE_USER": os.getenv("ORACLE_USER"),
        "ORACLE_PASS": os.getenv("ORACLE_PASS"),
        "ORACLE_DSN": os.getenv("ORACLE_DSN"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
