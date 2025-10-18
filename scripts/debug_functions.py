from core.logger import Logger
from core.middleware import adbScript
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization



@adbScript
def getScreenDump(adb: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs) -> bool:
    try: print(adb.getScreenDump())
    except Exception as e: print(e)

    return True


@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    try: adbClient.fastText(text)
    except Exception as e: print(e)

    return True