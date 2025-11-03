import random
import time
from functools import wraps
from json import JSONDecodeError
from typing import Tuple, Callable, Any, Optional
import bs4
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
import json

from core.hardware import AdbClient, Dot



class _AdbAutomatizationInterface:
    """
        Interface for AbAutomatization annotation
    """
    pass


POST_ACTION_CONTRACT = Callable[[AdbClient, _AdbAutomatizationInterface, bs4.element.Tag, *tuple[Any]], bool]

def postAction(function: POST_ACTION_CONTRACT):
    """
        Type of functions that can be called from waitUntil functions or after any other conditions.

    """

    @wraps(function)
    def wrapper(adbClient: AdbClient, adbAuto: AdbAutomatization, *args, **kwargs):
        if hasattr(AdbAutomatization, function.__name__):
            raise Exception("Cannot call AdbAutomatization method like a post action function (to avoid recursion).")

        result = function(adbClient, adbAuto, *args, **kwargs)
        return result

    return wrapper



class AdbAutomatization(_AdbAutomatizationInterface):
    """
        Automatization for simple hardware processes, works via ADB (hardware client)
        AdbClient wrapper - for more functionality
        Isolated, each only for one client
        Parser, randomizer (for delays) and hardware controller in one class
    """

    def __init__(self, adbClient: AdbClient, parsingMethod: str='lxml'):
        self._parsingMethod = parsingMethod
        self._adbClient: AdbClient = adbClient


    @property
    def screenDump(self) -> str:
        """
            Current screen dump.
        """
        return self._adbClient.getScreenDump()


    def randomDelay(self, *args) ->  float:
        """
            Make delay by gotten args.
            1 arg - set delay
            2 args - random delay, from arg 0 to arg 1
            > 2 args - random delay, will be chosen by choice method
            no args - 1-second delay
        """
        delay: float = 1.0 # base delay, will be changed by inputted args

        if len(args) == 1: delay = args[0]
        elif len(args) == 2: delay = random.randint(*args)
        elif len(args) > 2: delay = random.choice(args)

        time.sleep(delay)
        return delay

    # inner parser
    def getDumpSoup(self, dump: str) -> bs4.BeautifulSoup:
        return BeautifulSoup(dump, self._parsingMethod)


    def getDumpElement(self, dump: str, attrs: dict[str, str]) -> Optional[bs4.element.Tag]:
        """
            Find element by its inner attributes.
            For example:
            Element: <node text="Hello" id="12"></node>
            Attrs: {"text": "Hello", "id": 12}
        """

        soup = self.getDumpSoup(dump)
        return soup.find('node', attrs=attrs)


    def getElementBounds(self, element: bs4.element.Tag) -> Optional[Tuple[Dot, Dot, Dot]]:
        """
            Get bounds (coordinates) of element by its inner attributes.
            Example:
            0, 0    ___   30, 0
                   |___|
            0, 15         30, 15

            Output:
                1: Dot(0, 0) - start point (top, left)
                2: Dot(30, 15) - end point (bottom, right)
                3: Dot(8, 15) - center
            Returns in NON-RANDOM mode!
        """

        elementBounds: str = element.get('bounds')
        if not elementBounds: return None

        # convert to list using json loads (in json format only!)
        try:
            x1, y1, x2, y2 = json.loads( elementBounds.replace('][', ',') )
        except (ValueError, JSONDecodeError): return None

        elementCenter = ( (x1 + x2) / 2 , (y1 + y2) / 2 )
        # return Dot(*elementCenter), x2 - x1, y2 - y1 - OLD FORMAT
        return Dot(x1, y1), Dot(x2, y2), Dot(elementCenter[0], elementCenter[1])


    def clickInRect(self, dotTop: Dot, dotBottom: Dot, *_, clickDuration: Optional[int]=None) -> bool:
        """
            Randomly click in rectangle sector.
            Take sector by its top and bottom positions.
            dotTop - top, left position
            dotBottom - bottom, right position
            clickDuration - duration of the click. If none - ordinary click. IN SECONDS
            Other args will be ignored (to use it with other func just by *).
        """

        width, height = abs(dotBottom.x - dotTop.x), abs(dotBottom.y - dotTop.y)

        # get random values to click randomly
        randomX, randomY = map(lambda x: random.randint(0, x), (width, height))

        # click by new dot
        clickDot = Dot(dotTop.x + randomX, dotTop.y + randomY)
        return self._adbClient.swipe(clickDot, clickDot, swipeTime=clickDuration) \
            if clickDuration else self._adbClient.tap(clickDot)


    def swipeInRect(self, dotTop: Dot, dotBottom: Dot, *_, swipeDuration: int=1, direction: bool=True) -> bool:
        """
            Swipe by random vector in rectangle sector.
            Take sector by its top and bottom positions.
            dotTop - top, left position
            dotBottom - bottom, right position
            swipeDuration - duration of the swipe (time in seconds, 1000 ms = 1 sec)
            direction - the direction of the swipe. If direction is True - swipe to top. Else - swipe to bottom.
            Other args will be ignored (to use it with other func just by *).
        """

        # get rectangle position
        x1, y1 = dotTop.x, dotTop.y
        x2, y2 = dotBottom.x, dotBottom.y

        rand1 = random.randint(x1, x2)
        rand2 = random.randint(x1, x2)

        # create dots and swipe by themes
        dot1, dot2 = Dot(rand1, y1).make_random(), Dot(rand2, y2).make_random()
        if not direction: dot1, dot2 = dot2, dot1

        return self._adbClient.swipe(dot1, dot2, swipeTime=swipeDuration)


    def waitForElement(self, attrs: dict[str, str], delay: float=0.5, postActions: tuple[POST_ACTION_CONTRACT]=(), *args) -> bool:
        """
            Wait until element will be found.
            Looking for element by its inner attributes via beautiful soup.
            delay - sleep action between every iteration.
            Also has a past actions solution.
            Can start functions (which was decorated as post action) after finding element.
            args - arguments proxy to post actions.

            Returns True if all post actions were successful. False - if not.
        """

        element: bs4.element.Tag

        while True:
            # getting page dump and its soup
            currentDump: str = self.screenDump
            element = self.getDumpElement(currentDump, attrs)
            if element: break # if element was found

            # waiting before new iterations
            time.sleep(delay)

        # check for post actions
        try:
            if len(postActions) > 0:
                for action in postActions:
                    if not action(self._adbClient, self, element, *args):
                        return False
        except Exception as error: print(error)

        return True




class PostActions:
    """
        Built-in post actions.
    """

    @classmethod
    @postAction
    def clickOnElement(cls, adbClient: AdbClient, adbAuto: AdbAutomatization, element) -> bool:
        bounds = adbAuto.getElementBounds(element)
        if not bounds: return False

        return adbAuto.clickInRect(*bounds)


