import multiprocessing

import uvicorn
from dotenv import load_dotenv

from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization

load_dotenv()
import os

# need to create_all! delete after adding migrations
from db.data import *
from core.tasks.task import Task

from core.loader import Loader



def main():
    from db.connector import DatabaseConnector
    DatabaseConnector().create_all()

    # start admin panel. run this in new process (its gonna block it)
    def startDatabaseAdminPanel():
        from views import app
        uvicorn.run(app, host="0.0.0.0", port=8000)

    databaseAdminPanelProcess = multiprocessing.Process(target=startDatabaseAdminPanel)
    databaseAdminPanelProcess.start()

    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )
    core = loader.core

    def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
        adbClient.fastText(text)
        return True

    core.addTaskToService('9887a836545a593453@3c067526', testFunc,'Hello world!')


if __name__ == "__main__": main()
