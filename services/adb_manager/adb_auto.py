import random
import time
from dataclasses import dataclass, field
from typing import Tuple, Callable, Any, Optional

import bs4
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
import json

from services.adb_manager import AdbClient, Dot




class AdbAutomatization:
    """
        Automatization for screen dump parsing, works via ADB (adb client)
        Isolated, each only for one client
    """

    def __init__(self, adbClient: AdbClient):
        self._adbClient: AdbClient = adbClient

    def _getRandomDelay(self, *delay: tuple[float]) -> float:
        return random.randint(
            *map(lambda x: int(x * 1000), sorted(delay))
        ) / 1000


    # SCREEN ANALYZE METHODS

    def getScreenDump(self) -> str:
        return self._adbClient.getScreenDump()

    def findElement(self, dump: str, elementAttrs: dict[str, str]) -> Optional[Tuple[Dot, int, int]]:
        element = self.getElementSoup(dump, elementAttrs)
        if not element: return None

        elementBounds = element.get('bounds')
        if not elementBounds: return None

        x1, y1, x2, y2 = json.loads(elementBounds.replace('][', ','))
        elementCenter = ( (x1 + x2) / 2 , (y1 + y2) / 2 )
        return Dot(*elementCenter), x2 - x1, y2 - y1

    def getElementSoup(self, dump: str, elementAttrs: dict[str, str]) -> Optional[bs4.BeautifulSoup]:
        soup = BeautifulSoup(dump, 'lxml')
        element = soup.find('node', attrs=elementAttrs)
        return element


    def clickOnElement( self,
            elementAttrs: dict[str, str],
            delay: tuple[float]=(0.2, 0.6),
            randomizK: float=0.3, xCorrector: int=0, yCorrector: int=0,
            longClick=False, longClickDelay: float=0.2,
            dump: Optional[str]=None ) -> bool:

        dump = dump if dump else self.getScreenDump()
        findResult = self.findElement(dump, elementAttrs)
        if not findResult: return False

        elDot, elW, elH = findResult
        elDot.x = elDot.x + xCorrector
        elDot.y = elDot.y + yCorrector
        elDot = Dot(elDot.x, elDot.y).make_random(l_x=int(elW * randomizK), l_y=int(elH * randomizK))

        adbResult = self._adbClient.swipe(elDot, elDot, swipeTime=longClickDelay) if longClick else self._adbClient.tap(elDot)

        # adding delay between actions
        time.sleep(self._getRandomDelay(*delay))
        return adbResult


    def waitAndClickOnElement(self, elementAttrs: dict[str, str], iterCount=10, delay: tuple[float]=(0.5, 1)) -> bool:
        attempt, res = 0, False

        while not res and attempt != iterCount:
            res = self.clickOnElement(elementAttrs, delay)
            attempt += 1

        return res