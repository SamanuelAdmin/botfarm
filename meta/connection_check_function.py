from core.hardware import AdbClient
from core.logger import Logger


logger = Logger()
CHECKING_COMMAND = 'ping -c 1 -W 1 google.com'

def connectionCheckFunction(adb: AdbClient) -> bool:
    """
        Function for adb checker (waining checker).
        Returns True if client is connected to the internet.
    """
    result: bool = False

    try:
        commandResult = adb.sendAdbCommand(CHECKING_COMMAND)
        logger.info(str(commandResult))
    except Exception as e:
        logger.debug(f'{adb.serial} Got unexpected exception in internetChecker func: {e}')
    finally:
        return result