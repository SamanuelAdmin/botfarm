from core.logger import Logger
from core.middleware.decorators import adbScript
from services.adb_manager import AdbClient, Dot
from services.adb_manager.adb_auto import AdbAutomatization


logger = Logger(setDatetime=False)


@adbScript
def getScreenDump(adb: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs) -> bool:
    try:
        logger.debug(adb.getScreenDump())
    except Exception as e:
        logger.error(e)

    return True


@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    try:
        adbClient.fastText(text)
        logger.debug('Done')
    except Exception as e: logger.error(e)

    return True


@adbScript
def testSwipe(adbClient: AdbClient, adbAuto: AdbAutomatization) -> bool:
    adbAuto.swipeInRect(
        Dot(300, 500), Dot(600, 1000), direction=False
    )


@adbScript
def testEmojisInput(adbClient: AdbClient, adbAuto: AdbAutomatization, text) -> bool:
    adbClient.sendAdbCommand(f'am broadcast -a clipper.set -e text "{text}"')
    adbClient.sendAdbCommand('input keyevent 279')
    logger.debug(adbClient.serial, f'Done.')
    return True