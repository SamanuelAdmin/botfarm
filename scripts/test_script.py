from core.middleware.decorators import adbScript
from core.hardware import AdbClient
from core.hardware import AdbAutomatization



@adbScript
def testFunc(adbClient: AdbClient, adbAuto: AdbAutomatization, text: str) -> bool:
    adbClient.fastText(text)
    return True

if __name__ == '__main__':
    pass