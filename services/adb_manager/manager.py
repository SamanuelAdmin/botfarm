import os
import random
import shlex
import time
import json
from typing import Optional, Any

from .api_connector import ApiConnector
from .exceptions import *
from .meta.dot import Dot



class AdbClient:
    def __init__(
            self, connector: ApiConnector,
            serial: str, deviceLinkPattern: str='/device/{}'
    ):
        self.serial = serial
        self.connector = connector
        self.deviceLink = deviceLinkPattern.format(serial)

    def sendAdbCommand(self, command: str, daemon: bool=False, timeout: Optional[float]=None) -> dict[str, Any]:
        response = self.connector.apiRequest(
            self.deviceLink, data=json.dumps({
                'command': command, 'daemon': daemon
            }), method='post', timeout=timeout
        )

        if isinstance(response, int):
            raise IncorrectStatusCodeException(response, url=self.deviceLink)
        elif response.get('status') != True:
            raise IncorrectStatusCodeException(response)

        return response

    def tap(self, dot: Dot) -> bool:
        return bool(
            self.sendAdbCommand(
                f'input tap {dot.x} {dot.y}'
            )
        )

    def swipe(self, dotStart: Dot, dotFinish: Dot, timeK: float=0.02, swipeTime: Optional[float]=None) -> bool:
        swipeTime = swipeTime * 1000 if swipeTime else int((dotFinish - dotStart) * timeK)
        return bool(
            self.sendAdbCommand(
                f'input swipe {dotStart} {dotFinish} {swipeTime}'
            )
        )

    def text(self, message: str, delayMicros: tuple[int]=(40, 90)) -> bool:
        for letter in message:
            match letter:
                case '"': letter = '\\"'
                case ' ': letter = '%s'

            self.sendAdbCommand( f'input text "{letter}"', daemon=True )
            time.sleep(
                random.randint(delayMicros[0], delayMicros[1]) / 1000
            )

        return True

    def getScreenDump(self) -> str:
        resp = self.sendAdbCommand(
            f'uiautomator dump /dev/tty'
        )
        xmlData = resp.get('result')

        if xmlData is None: raise ResultNotFoundException(resp)
        return xmlData[:xmlData.rfind('>')+1]

    def makeScreenshot(self, filepath: str='/sdcard/screen.png') -> bool:
        return bool(self.sendAdbCommand(f'screencap -p {filepath}'))


    def downloadFile(self, filename: str='/sdcard/screen.png', downloadDir: Optional[str]=None) -> str|None:
        filename = self.sendAdbCommand( f'adb_pull {filename}' ).get('result')
        downloadDir = downloadDir or os.getcwd()
        fullPath = os.path.join(downloadDir, filename)

        try:
            fileResponse = self.connector.apiRequest(f'/file/get/{filename}')

            with open(fullPath, 'wb') as file:
                dataStream = fileResponse.iter_content(chunk_size=8192)
                for data in dataStream:
                    file.write(data)

            return fullPath
        except Exception as e: raise FileDownloadException(fullPath)

        return None


    def fastText(self, message: str, delay: tuple[int, int]=(0.01, 0.07)) -> bool:
        safe_message = shlex.quote(message)

        cmd = (
            f's={safe_message}; '
            'i=0; len=${#s}; '
            'while [ $i -lt $len ]; do '
            'c=$(echo "$s" | cut -c$((i+1))); '
            'input text "$c"; '
            f'sleep $(awk -v min={delay[0]} -v max={delay[1]} "BEGIN{{srand(); print min+rand()*(max-min)}}"); '
            'i=$((i+1)); '
            'done'
        )

        # default timeout - 1 second for every symbol, it also can give 408 status code (response timeout)
        return bool(self.sendAdbCommand(cmd, timeout=1*len(safe_message)))

    def deleteText(self, length: int=1, fast: bool=False, sec: float=0.5) -> bool:
        self.sendAdbCommand('input keyevent KEYCODE_MOVE_END')

        if not fast:
            for _ in range(length):
                if not bool(self.sendAdbCommand(f'input keyevent KEYCODE_DEL')):
                    return False
        else:
            if not bool(
                    self.sendAdbCommand(
                        'input keyevent KEYCODE_DEL --longpress $(printf "KEYCODE_DEL %.0s" {1..' + str(sec * 1000) + '})'
                    )
                ): return False

        return True


# ADB HUB API
class Manager:
    def __init__(self, api: str, timeout: float=2):
        self.api = api
        self._timeout = timeout
        self.apiConnector = ApiConnector(api, timeout=self._timeout)
        self._adbClients: dict[str, AdbClient] = {}

    # ADB HUB INFO
    def getUUID(self) -> str|None:
        response =  self.apiConnector.apiRequest(
            '/all/id'
        )
        if type(response) is int: raise IncorrectStatusCodeException(response)
        return response.get('result')


    # CREATE AND READ FOR ALL CLIENTS
    def getAllSerials(self) -> list[str]|list:
        response =  self.apiConnector.apiRequest(
            '/all/all'
        )
        if type(response) is int: raise IncorrectStatusCodeException(response)

        if response.get('status') != True: return []
        return response.get('result') if response.get('result') else []

    def getAllLoadedSerials(self) -> dict[str, AdbClient]:
        return self._adbClients

    def loadAllSerials(self) -> None:
        serials = self.getAllSerials()

        for serial in serials:
            self._adbClients[serial] = AdbClient(self.apiConnector, serial)


    # CREATE AND READ FOR 1 CLIENT
    def loadSerial(self, serial: str) -> AdbClient:
        adbClient = AdbClient(self.apiConnector, serial)
        self._adbClients[serial] = adbClient
        return adbClient

    def getClient(self, serial: str) -> AdbClient|None:
        return self._adbClients.get(serial)


