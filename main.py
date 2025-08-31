from Cryptodome.SelfTest.Cipher.test_OFB import new_func
from fastapi import FastAPI

from services.adb_manager import AdbManager, AdbClient
from views import MainApp
import uvicorn

from services.accounts_manager import AccountsManager
from services.insta_api.api_account_manager import ApiAccountManager


def loginScript(adb: AdbClient):
    currentScreen = adb.getScreenDump()
    


def main():
    m = AdbManager('http://184.82.145.229:18100')
    adb = m.loadSerial('98897a314e31434343')
    loginScript(adb)


if __name__ == "__main__": main()
