import multiprocessing
import time
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from scripts.selling_services_scripts import followAccount

load_dotenv()
import os, sys

from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization
# need to create_all! delete after adding migrations
from db.data import *
from core.loader import Loader
from core.middleware import adbScript
from core.logger import Logger, setup_default_logger



def getArgByFlag(args: list[str], flag: str) -> str|bool:
    """
        Getting data by flag, from any list. Use it for getting console command args.
    :param args: List with arguments.
    :param flag: Flag (usually started with "-")
    :return: False if arg not found, True is flag has no data after itself, str - if flag`s data found.
    """
    # if flag not found
    if flag not in args: return False

    dataIndex: int = args.index(flag) + 1
    # if flag is the last element at the list
    if dataIndex >= len(args): return True

    # getting data by index
    data: Optional[str] = args[dataIndex]
    # is the next element is a flag
    if data[0] == flag[0]: return True
    return data


def startDatabaseAdminPanel():
    # start admin panel. it is going to block process
    from views import app
    uvicorn.run(app, host="0.0.0.0", port=8000)


@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    adbClient.fastText(text)
    return True

def main():
    clArgs = sys.argv[1:]
    mode = getArgByFlag(clArgs, "-mode")

    from db.connector import DatabaseConnector
    DatabaseConnector().create_all()

    # init base logger and create local logger object instance (for this file only)
    setup_default_logger()
    logger = Logger()

    if mode == "debug":
        # block main process by starting admin panels and API
        startDatabaseAdminPanel()
        # exiting
        return
    else:
        # let system start correctly, without blocking
        databaseAdminPanelProcess = multiprocessing.Process(target=startDatabaseAdminPanel)
        databaseAdminPanelProcess.start()

    
    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )
    core = loader.core
    core.start()

    for serviceId in core.servicesTable:
        core.addTaskToService(
            #'9889ba304138394552@3c067526',
            serviceId,
            followAccount, 'https://www.instagram.com/psptm5/'
        )

    time.sleep(60)
    core.stop()


if __name__ == "__main__": main()
