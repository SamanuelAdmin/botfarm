import random
import shlex
import time
import json

from .api_connector import ApiConnector
from .exceptions import *
from .meta.dot import Dot


class AdbClient:
    def __init__(
            self, connector: ApiConnector,
            serial: str, deviceLinkPattern: str='/device/{}'
    ):
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

    def swipe(self, dotStart: Dot, dotFinish: Dot, timeK=0.6) -> bool:
        swipeTime = (dotFinish - dotStart) * timeK
        return bool(
            self.sendAdbCommand(
                f'input swipe {dotStart} {dotFinish} {swipeTime}'
            )
        )

    def text(self, message: str, delayMicros: list=[40, 90]) -> bool:
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


    def fastText(self, message: str, delay: list=[0.01, 0.07]) -> bool:
        # message = message.replace('"', '\\"')\
        #             .replace(' ', '%s')

        # return self.sendAdbCommand(
        #     f's="{message}"; min={delay[0]}; max={delay[1]}; ' \
        #     + '''for ((i=0;i<${#s};i++)); do input text "${s:i:1}"; sleep $(awk -v min=$min -v max=$max 'BEGIN{srand(); print min+rand()*(max-min)}'); done'''
        # )

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

        return self.sendAdbCommand(cmd)


class Manager:
    def __init__(self, api: str):
        self.api = api
        self.apiConnector = ApiConnector(api)
        self._adbClients = {}

    def getAllSerials(self) -> list:
        response =  self.apiConnector.apiRequest(
            '/all/all'
        )

        if response.get('status') != True: return []
        return response.get('result') if response.get('result') else []

    def loadAllSerials(self):
        serials = self.getAllSerials()

        for serial in serials:
            self._adbClients[serial] = AdbClient(self.apiConnector, serial)

    def getSerial(self, serial: str) -> str:
        return self._adbClients.get(serial)

    def loadSerial(self, serial: str) -> AdbClient:
        return AdbClient(self.apiConnector, serial)

