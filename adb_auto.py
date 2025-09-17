import random
import time
from dataclasses import dataclass, field
from typing import Tuple, Callable, Any, Optional
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
import json

from services.adb_manager import AdbManager, AdbClient, Dot



@dataclass
class ScriptAction:
    name: str
    function: Callable[[Any], bool]
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)




class AdbAutoManager:
    def __init__(self, adbManager: AdbManager):
        self._adbManager = adbManager
        self._adbManager.loadAllSerials()

    def _getRandomDelay(self, delay: list[float]) -> float:
        return random.randint(
            *map(lambda x: int(x * 1000), sorted(delay))
        ) / 1000

    def getScreenDump(self, serial: str, client=None) -> str:
        if not client:
            client: AdbClient = self._adbManager.getClient(serial)

        return client.getScreenDump()


    def findElement(self, dump: str, elementAttrs: dict[str, str]) -> Tuple[Dot, int, int]|None:
        soup = BeautifulSoup(dump, 'lxml')
        element = soup.find('node', attrs=elementAttrs)
        if not element: return None

        elementBounds = element.get('bounds')
        if not elementBounds: return None

        x1, y1, x2, y2 = json.loads(elementBounds.replace('][', ','))
        elementCenter = ( (x1 + x2) / 2 , (y1 + y2) / 2 )
        return Dot(*elementCenter), x2 - x1, y2 - y1


    def clickOnElement(self, elementAttrs: dict[str, str], serial: str=None, delay: list[float]=[0.2, 0.6], client: Optional[AdbClient]=None, randomizK: float=0.3) -> bool:
        if not client:
            client: AdbClient = self._adbManager.getClient(serial)
            serial = client.serial

        dump = self.getScreenDump(serial, client=client)
        findResult = self.findElement(dump, elementAttrs)
        if not findResult: return False

        elDot, elW, elH = findResult
        elDot = Dot(elDot.x, elDot.y).make_random(l_x=int(elW * randomizK), l_y=int(elH * randomizK))

        adbResult = client.tap(elDot)

        # adding delay betweek actions
        time.sleep(self._getRandomDelay(delay))
        return adbResult

    def waitAndClickOnElement(self, serial: str, elementAttrs: dict[str, str], iterCount=10, delay: list[float]=[0.5, 1]) -> bool:
        attempt, res = 0, False

        while not res and attempt != iterCount:
            res = self.clickOnElement(serial, elementAttrs, delay)
            attempt += 1

        return res


    def scriptActionsWithoutErrors(self, actions: list[ScriptAction]) -> dict[str, bool]:
        resultsLogs = {}

        for action in actions:
            actionResult = action.function(
                *action.args,
                **action.kwargs
            )

            resultsLogs[action.name] = actionResult
            if not actionResult: break

        return resultsLogs