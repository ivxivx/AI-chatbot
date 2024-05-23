import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.dirname(__file__) + "/.env")

def set_environment():
  variable_dict = globals().items()
  for key, value in variable_dict:
    # print(key, value)
    if "API" in key or "ID" in key:
      os.environ[key] = value

