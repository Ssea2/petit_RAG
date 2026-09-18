import fastapi
from fastapi.routing import APIRoute
import uvicorn

from dotenv import load_dotenv

load_dotenv()

from utils.bdd.manager import bdd_manager
from utils.config_loader import API_config

config = API_config()


bdd_manager(config=config).add_documents(["requirements.txt"])



