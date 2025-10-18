import multiprocessing
import time
from typing import Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()
import os, sys

from scripts import debug_functions
# need to create_all! delete after adding migrations
from core.loader import Loader
from core.logger import Logger, setup_default_logger

from scripts import debug_functions
from scripts.login_script import loginScript



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

    # for i in range(1):
    core.addTaskToService(
        #'9889ba304138394552@3c067526', core.servicesTable[i]
        '98882935425939524a@3c067526', debug_functions.testFunc, 'Hello World! Hello World! Hello World!'
        # 'ms.jason.bakers25731', 'RLpk6jDCSrEt', '4Q3FI3OTH7VYVRJGFJFZZ4NJ6GZSDRFQ'
    )

    time.sleep(60)
    core.stop()


if __name__ == "__main__": main()
