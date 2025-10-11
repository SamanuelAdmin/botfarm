from core.middleware import adbScript
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization



@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    adbClient.fastText(text)
    return True

if __name__ == '__main__':
    pass