import uvicorn
from dotenv import load_dotenv
load_dotenv()
import os

# need to create_all! delete after adding migrations
from db.data import *

from core.loader import Loader



def main():
    from db.connector import DatabaseConnector
    DatabaseConnector().create_all()

    # TODO: START SHIT IN NEW PROCESS
    # from views import app
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )
    core = loader.core


if __name__ == "__main__": main()
