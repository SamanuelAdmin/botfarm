from core.logger import Logger
from core.middleware import adbScript
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization


logger = Logger()


@adbScript
def getScreenDump(adb: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs):
    logger.debug(adb.getScreenDump())


@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    adbClient.fastText(text)
    return True