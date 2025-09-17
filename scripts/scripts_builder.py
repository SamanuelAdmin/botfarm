import copy
import random
import time
from datetime import datetime
from typing import Optional

import numpy as np
import cv2

from services.adb_manager import AdbManager, Dot, AdbClient
from services.ui_recognizer import Recognizer
from adb_auto import AdbAutoManager



def loadScreenShotAsCv2(adb: AdbClient) -> np.ndarray|None:
    adb.makeScreenshot()
    path = adb.downloadFile()
    return cv2.imread(path) if path else None

def tapBy4Numbers(adb: AdbClient, args: tuple[int]|list[int]) -> bool:
    adb.tap(
        Dot(
            int(args[0] + args[2] / 2),
            int(args[1] + args[3] / 2)
        ).make_random(int(args[2] / 2), int(args[3] / 2))
    )

def randomDelay(*args):
    if len(args) == 1: time.sleep(args[0])
    elif len(args) == 2: time.sleep( random.randint(*args) )
    elif len(args) > 2: time.sleep( random.choice(args) )


def checkRecognizedTextValues(result: dict[str, list[int]]) -> bool:
    return all(list(result.values())) and len(result) != 0

def checkTextOnScreen(adb: AdbClient, recognizer: Recognizer, text: str) -> bool:
    text = text.lower().split(' ')
    screen = loadScreenShotAsCv2(adb)
    recognitionResult = recognizer.findTextOnImage(screen, text)

    return checkRecognizedTextValues(recognitionResult)


def clickViaTemplate(adb: AdbClient, recognizer: Recognizer, templateName: str) -> bool|list[int]:
    screen = loadScreenShotAsCv2(adb)
    elementCords = recognizer.findTemplateOnImage(screen, templateName)
    if not elementCords: return False

    tapBy4Numbers(adb, elementCords)
    return elementCords


def clickViaScreenText(adb: AdbClient, recognizer: Recognizer, text: str, xCorrector=0, yCorrector=0) -> bool|list[int]:
    text = text.lower().split(' ')

    screen = loadScreenShotAsCv2(adb)
    clickableTextParts = recognizer.findTextOnImage(screen, text)

    if not checkRecognizedTextValues(clickableTextParts):
        return False

    textCenters = [
        ( int(part[0] + part[2] / 2), int(part[1] + part[3] / 2) ) \
        for part in clickableTextParts.values()
    ]

    clickableX, clickableY = [
        sum([el[0] for el in textCenters]) / len(textCenters),
        sum([el[1] for el in textCenters]) / len(textCenters),
    ]

    cords = [clickableX + xCorrector, clickableY + yCorrector, 10, 2]
    tapBy4Numbers(adb, cords)
    return cords


def smallSwipe(adb):
    adb.swipe(
        Dot(random.randint(300, 500), 900).make_random(l_x=15, l_y=15),
        Dot(random.randint(350, 450), 600).make_random(l_x=15, l_y=15),
        timeK=0.05
    )


def waitUntilTextFind(adb: AdbClient, recognizer, text: str, iter: int=-1) -> bool:
    iter = copy.copy(iter)

    while iter != 0:
        iter -= 1
        randomDelay(1)
        if checkTextOnScreen(adb, recognizer, text): return True

    return False


def swipeUntilFindElement(
        adb: AdbClient, recognizer: Recognizer,
        text: Optional[str]=None, templateName: Optional[str]=None,
        dumpAttrs: Optional[dict[str, str]]=None, adbAuto: Optional[AdbAutoManager]=None,
        iter=-1 ) -> bool:
    assert any([text, templateName, dumpAttrs])
    iter = copy.copy(iter)

    while iter != 0:
        iter -= 1; randomDelay(1)
        screen = loadScreenShotAsCv2(adb)

        if text: recognitionResult = checkTextOnScreen(adb, recognizer, text)
        elif templateName: recognitionResult = recognizer.findTemplateOnImage(screen, templateName)
        elif dumpAttrs: recognitionResult = adbAuto.findElement( adb.getScreenDump(), dumpAttrs )
        else: return False

        if recognitionResult: return True
        smallSwipe(adb)

    return False


def waitForDumpElement(adb: AdbClient, adbAuto: AdbAutoManager, elementAttrs: dict[str, str], iter: int=-1) -> bool|list[int]:
    iter = copy.copy(iter)

    while iter != 0:
        iter -= 1
        randomDelay(1)
        element = adbAuto.findElement( adb.getScreenDump(), elementAttrs=elementAttrs )
        if element: return element

    return False


def simpleLog(adb: AdbClient, *logs):
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{currentTime}] {adb.serial} - ', *logs)


def goToProfilePage(adb: AdbClient, adbAuto: AdbAutoManager) -> bool:
    return adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': 'Profile'}, randomizK=0.2)