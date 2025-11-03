import os
import random
import shlex
import time
import json
from collections.abc import Callable
from functools import wraps
from typing import Optional, Any

from core.logger import Logger
from services.adb_manager.api_connector import ApiConnector
from services.adb_manager.exceptions import *
from services.adb_manager.meta.dot import Dot


logger = Logger()

class AdbClient:
    """
        "API" for low-level (hardware) phone controlling.
    """

    def __init__(
            self, connector: ApiConnector,
            serial: str, deviceLinkPattern: str='/device/{}'
    ):
        self.serial = serial
        self.connector = connector
        self.deviceLink = deviceLinkPattern.format(serial)
        # phone`s clipboard API, can be used from "outside"
        self._bufferProcessor = None


    @property
    def bufferProcessor(self):
        """ Added because buffer is an option. Also, it needs time to make a request when initing """

        if self._bufferProcessor is None:
            logger.info(self.serial, 'Initializing buffer processor...')
            self._bufferProcessor = self.BufferProcessor(self)

        return self._bufferProcessor


    class BufferProcessor:
        """
            Phone`s clipboard manager. Inner class for AdbClient
        """
        _clipperStatus: bool # true if already installed and false if not

        def __init__(self, adbClient):
            self._adbClient = adbClient

            # check if clipper installed and start it
            try:
                self._adbClient.sendAdbCommand( 'am startservice ca.zgrs.clipper/.ClipboardService' )
                self._clipperStatus = True
            except IncorrectStatusException:
                logger.error(f'{self._adbClient.serial} Cannot start clipboard service (clipper).')
                self._clipperStatus = False


        def clipperRequired(function: Callable):
            """
                Checks if clipped has been installed and started.
                Raises Exception if not.
            """

            @wraps(function)
            def wrapper(bufferProcessor, *args, **kwargs):
                if not bufferProcessor._clipperStatus:
                    raise Exception(
                        'Cannot find clipper! Maybe its not installed? Please install it from https://github.com/majido/clipper'
                    )

                return function(bufferProcessor, *args, **kwargs)
            return wrapper


        @clipperRequired
        def copy(self, text: str) -> bool:
            """ Set the text to the clipboard. """
            return self._adbClient.sendAdbCommand(f'am broadcast -a clipper.set -e text "{text}"')

        @clipperRequired
        def paste(self) -> bool:
            """ Paste text from the clipboard (Usually to the text field).
                Returns only processing status! """
            return self._adbClient.sendAdbCommand('input keyevent 279')

        @clipperRequired
        def get(self) -> str:
            """ Get string data from the buffer. """
            return self._adbClient.sendAdbCommand('am broadcast -a clipper.get')



    def sendAdbCommand(self, command: str, daemon: bool=False, timeout: Optional[float]=None) -> dict[str, Any]:
        """
            Sending adb command, from "command" attribute.
            Daemon - start command as a daemon thread (if true).
            Timeout - optional timeout for the server`s response (for long commands).
        """
        response = self.connector.apiRequest(
            self.deviceLink, data=json.dumps({
                'command': command, 'daemon': daemon
            }), method='post', timeout=timeout
        )

        if isinstance(response, int):
            raise IncorrectStatusCodeException(response, url=self.deviceLink)
        elif response.get('status') != True:
            raise IncorrectStatusException(response)

        return response

    def tap(self, dot: Dot) -> bool:
        """ Click on the screen. """
        return bool(
            self.sendAdbCommand(
                f'input tap {dot.x} {dot.y}'
            )
        )

    def swipe(self, dotStart: Dot, dotFinish: Dot, timeK: float=0.02, swipeTime: Optional[int]=None) -> bool:
        # swipe time in seconds (CANNOT BE FLOAT (IDK WHY))
        swipeTime = swipeTime * 1000 if swipeTime else int((dotFinish - dotStart) * timeK)
        return bool(
            self.sendAdbCommand(
                f'input swipe {dotStart} {dotFinish} {swipeTime}'
            )
        )

    def text(self, message: str, delayMicros: tuple[int]=(40, 90)) -> bool:
        """ Not optimized realization for text inputting. """
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
        """ Get screen dump in xml format. """
        resp = self.sendAdbCommand(
            f'uiautomator dump /dev/tty', timeout=100
        )
        xmlData = resp.get('result')

        if xmlData is None: raise ResultNotFoundException(resp)
        return xmlData[:xmlData.rfind('>')+1]


    def makeScreenshot(self, filepath: str='/sdcard/screen.png') -> bool:
        return bool( self.sendAdbCommand(f'screencap -p {filepath}') )

    def downloadFile(self, filename: str='/sdcard/screen.png', downloadDir: Optional[str]=None) -> str|None:
        # downloading file to the hub
        filename = self.sendAdbCommand( f'adb_pull {filename}' ).get('result')
        downloadDir = downloadDir or os.getcwd()
        fullPath = os.path.join(downloadDir, filename)

        try:
            # request download from the hub
            fileResponse = self.connector.apiRequest(f'/file/get/{filename}')

            with open(fullPath, 'wb') as file:
                for data in fileResponse.iter_content(chunk_size=8192):
                    file.write(data)

            return fullPath
        except Exception as e:
            raise FileDownloadException(fullPath)


    def fastText(self, message: str, delay: tuple[int, int]=(0.01, 0.07)) -> bool:
        """
            Optimized realization for text inputting.
            Can be configured as much as you want.
        """

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
        return bool( self.sendAdbCommand(cmd, timeout=1*len(safe_message)) )


    def _deleteLetter(self) -> bool:
        return bool(self.sendAdbCommand(f'input keyevent KEYCODE_DEL'))

    def deleteText(self, length: int=1, fast: bool=False, sec: float=0.5) -> bool:
        """ Deleting all text from the text field (by length in slow mode and using sec attribute in fast mode). """
        # going to the end of the text
        self.sendAdbCommand('input keyevent KEYCODE_MOVE_END')

        if fast:
            return bool(
                self.sendAdbCommand(
                    'input keyevent KEYCODE_DEL --longpress $(printf "KEYCODE_DEL %.0s" {1..' + str(sec * 1000) + '})'
                )
            )

        for _ in range(length):
            if not self._deleteLetter():
                return False
        else: return True



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


