from services.adb_manager import AdbManager, Dot, AdbClient
from adb_auto import AdbAutoManager

from scripts.login_script import loginScript




def main():
    TEST_SERIAL = '98893a363136463157'

    adbManager = AdbManager('https://e1ae0b9f37c7.ngrok-free.app')
    adbAuto = AdbAutoManager(adbManager)
    adb = adbManager.loadSerial(TEST_SERIAL)

    # login script
    # loginScript(adb, adbAuto, 'dr.kevinjohnsons51870', 'PASS', 'PASS')
    # print(adb.getScreenDump())

    # adb.makeScreenshot()
    # adb.downloadFile()




if __name__ == "__main__": main()
