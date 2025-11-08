import multiprocessing
import time
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from core.dispatcher import Dispatcher
from core.middleware.adb_checker import WaitingAdbChecker
from meta.connection_check_function import connectionCheckFunction
from services.db_services.order_manager import OrderManager
from services.panel_manager.manager import PanelManager

load_dotenv()
import os, sys

from scripts import debug_functions
# need to create_all! delete after adding migrations
from core.loader import Loader
from core.logger import Logger, setup_default_logger

from scripts import debug_functions
from scripts.login_script import loginScript
from scripts.selling_services_scripts import *
from scripts.edit_profile_info import editProfileInfoScript
from scripts.control_script import *


# some temp configs
DEBUG: bool = False


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
    global DEBUG

    clArgs = sys.argv[1:]
    mode = getArgByFlag(clArgs, "-mode")
    if mode == "debug": DEBUG = True

    from db.connector import DatabaseConnector
    DatabaseConnector().create_all()

    # init base logger and create local logger object instance (for this file only)
    setup_default_logger(debug=DEBUG)
    logger = Logger()


    # let system start correctly, without blocking
    databaseAdminPanelProcess = multiprocessing.Process(target=startDatabaseAdminPanel)
    databaseAdminPanelProcess.start()

    
    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )

    # pre configs
    WaitingAdbChecker.config(connectionCheckFunction)
    loader.setAdbChecker(WaitingAdbChecker)

    # main loading part
    loader.load()
    core = loader.core
    core.start()

    panelManager = PanelManager(OrderManager(), os.getenv('PANEL_API_KEY'))
    dispatcher = Dispatcher(core, panelManager)
    dispatcher.load()
    dispatcher.handler()

    # core.addServiceTask('988e9034574a4d5831@3c067526', parseActiveAccounts)
    # core.processService('988e9034574a4d5831@3c067526')


if __name__ == "__main__": main()
