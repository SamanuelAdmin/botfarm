import os
import random
import shlex
import time
import json
from typing import Optional

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

    def sendAdbCommand(self, command: str) -> dict[str, Any]:
        response = self.connector.apiRequest(
            self.deviceLink, data=json.dumps({
                'command': command
            }), method='post'
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

    def swipe(self, dotStart: Dot, dotFinish: Dot, timeK=0.02) -> bool:
        swipeTime = int((dotFinish - dotStart) * timeK)
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

            self.sendAdbCommand( f'input text "{letter}"' )
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
        except Exception as e: print(FileDownloadException(fullPath))

        return None


    def fastText(self, message: str, delay: tuple[int]=(0.01, 0.07)) -> bool:
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

        return bool(self.sendAdbCommand(cmd))


class Manager:
    def __init__(self, api: str):
        self.api = api
        self.apiConnector = ApiConnector(api)
        self._adbClients = {}

    def getAllSerials(self) -> list[str]|list:
        response =  self.apiConnector.apiRequest(
            '/all/all'
        )
        if type(response) is int: raise IncorrectStatusCodeException(response)

        if response.get('status') != True: return []
        return response.get('result') if response.get('result') else []

    def loadAllSerials(self) -> None:
        serials = self.getAllSerials()

        for serial in serials:
            self._adbClients[serial] = AdbClient(self.apiConnector, serial)

    def loadSerial(self, serial: str) -> AdbClient:
        adbClient = AdbClient(self.apiConnector, serial)
        self._adbClients[serial] = adbClient
        return adbClient

    def getClient(self, serial: str) -> AdbClient:
        return self._adbClients.get(serial)


