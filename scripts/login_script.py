"""
    Script with "modules" architecture.
    Processing method:
    1) Starting...
    2) Detector - detect "task" which you need to complete
    3) Doing task...
    4) Returns to detector and checking if it's finished.
"""

import random
import time
from typing import Optional

from core.logger import Logger
from core.middleware.decorators import adbScript
from core.middleware.decorators import ADB_SCRIPT_CONTRACT
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization, PostActions
from services.fa2 import get2FACode



logger = Logger(setDatetime=False)


def waitAndClick(adbAuto: AdbAutomatization, attrs: dict[str, str]) -> bool:
    """
        Function-adapter for simple "find-and-click" actions.
    """
    return adbAuto.waitForElement( attrs, postActions=(PostActions.clickOnElement,) )


@adbScript
def inputCredsPage(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, *args) -> bool:
    logger.debug(adb.serial, 'Inputting username...')

    adbAuto.waitForElement( { 'class': "android.widget.EditText" } )
    usernameField = adbAuto.getDumpElement( adbAuto.screenDump, { 'class': "android.widget.EditText" } )

    if len(usernameField.get('text')) > 0:
        logger.debug(adb.serial, 'Deleting old username...')
        adbAuto.clickInRect(*adbAuto.getElementBounds( usernameField ))
        waitAndClick(adbAuto, {'content-desc': "Clear Username, email or mobile number text"})

    waitAndClick(adbAuto, { 'class': "android.widget.EditText" })
    adb.fastText(login)
    logger.debug(adb.serial, 'Username entered.')

    logger.debug(adb.serial, 'Inputting password...')
    waitAndClick(adbAuto, { 'content-desc': "Password,", 'class': "android.widget.EditText" })
    adb.fastText(password)
    logger.debug(adb.serial, 'Password entered. Pressing Log in button...')

    waitAndClick(adbAuto, { 'content-desc': "Log in", 'class': "android.widget.Button" })
    return True


@adbScript
def fa2Page(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, fa2Secret: str) -> bool:
    logger.debug(adb.serial, 'Entering 2FA code...')
    waitAndClick(adbAuto, {'class': "android.widget.EditText", 'content-desc': "Code,"})

    FA2Code = get2FACode(fa2Secret)
    adb.fastText(FA2Code)

    logger.debug(adb.serial, 'Confirming 2fa code.')
    waitAndClick(adbAuto, {'content-desc': "Continue"})

    return True


@adbScript
def saveLoginInfoPage(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Do not save login info.')
    return waitAndClick(adbAuto, {'content-desc': "Not now", 'class': "android.widget.Button"})


@adbScript
def addInstagramAccount(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Adding instagram account.')

    for _ in range(2):
        adbAuto.swipeInRect(
        *adbAuto.getElementBounds(
                adbAuto.getDumpElement(
                    adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/recycler_view_container_id'}
                )
            ), direction=False
        )

    return waitAndClick(adbAuto, {'content-desc': "Add Instagram account", 'class': "android.widget.Button"})


@adbScript
def logIntoAccountButton(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Log into existing account.')
    return waitAndClick(adbAuto, {'content-desc': "Log into existing account", 'class': "android.widget.Button"})

@adbScript
def promoDialogDispatcher(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Clicking second button on the dialog field.')
    return waitAndClick(adbAuto, {'resource-id': "com.instagram.android:id/igds_promo_dialog_secondary_button"})

@adbScript
def accessToContactsPage(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Skipping access to contacts page.')
    return waitAndClick(adbAuto, {'content-desc': "Skip", 'class': "android.widget.Button"})

@adbScript
def disableLocationServices(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Disabling location.')

    waitAndClick(adbAuto, {'class': "android.widget.Button"})
    waitAndClick(adbAuto, {'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'})

    return True

@adbScript
def relevantAdsPage(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Close "relevant ADS page".')
    return waitAndClick(adbAuto, {'content-desc': "Close", 'class': "android.widget.Button"})

@adbScript
def logoutAfterConfirmation(adb: AdbClient, adbAuto: AdbAutomatization, login: str, *args) -> bool:
    logger.info(adb.serial, 'Leaving account.')

    waitAndClick(adbAuto, {'content-desc': 'Menu'})
    waitAndClick(adbAuto, {'text': f'Log out {login}'})

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'},
        postActions=( PostActions.clickOnElement, )
    )

    time.sleep(1)
    return True

@adbScript
def useAnotherProfile(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Using another account.')
    return waitAndClick(adbAuto, {'content-desc': 'Use another profile'})

@adbScript
def closeRemovedContentPage(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Closing removed content page.')
    return waitAndClick(adbAuto, {'content-desc': 'Cancel'})

@adbScript
def checkOnAnotherDevicePage(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Got "check on another device" page.')
    waitAndClick(adbAuto, {'content-desc': "Try another way"})
    waitAndClick(adbAuto, {'content-desc': "Authentication app"})
    waitAndClick(adbAuto, {'content-desc': "Continue"})

    return fa2Page(adb, adbAuto, *args)

@adbScript
def allowCookies(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Allowing cookies.')
    return waitAndClick(adbAuto, {'content-desc': 'Allow all cookies'})

@adbScript
def configuringAds(adb: AdbClient, adbAuto: AdbAutomatization, *args) -> bool:
    logger.info(adb.serial, 'Configuring ads.')
    waitAndClick(adbAuto, {'class': "android.widget.Button"})
    waitAndClick(adbAuto, {'content-desc': "Use free of charge with ads"})
    waitAndClick(adbAuto, {'content-desc': "Continue"})
    waitAndClick(adbAuto, {'text': "Agree"})
    waitAndClick(adbAuto, {'content-desc': "Close"})
    return True



# patterns for each element. required in modules architecture
# element_name : element_attrs
patterns: dict[str, dict[str, str]] = {
    'usernameTextField': { 'index': "0", 'class': "android.widget.EditText" },
    'passwordTextField': { 'content-desc': "Password,", 'class': "android.widget.EditText" },
    '2faLabel': {'text': "Go to your authentication app"},
    'saveLoginInfoPage': {'text': "Save your login info?"},
    'addInstagramAccountButton': {'resource-id': 'com.instagram.android:id/recycler_view_container_id'},
    'logIntoAccountButton': {'content-desc': 'Log into existing account'},
    'promoDialog': {'resource-id': 'com.instagram.android:id/igds_promo_dialog_headline'},
    'accessToContactsPage': {'text': 'Allow access to contacts to find people to follow'},
    'disableLocationServices': {'content-desc': 'To use Location Services, allow Instagram to access your location'},
    'relevantAdsPage': {'text': "Want us to show you ads that are more relevant by using your activity from ad partners?"},
    'useAnotherProfile': {'content-desc': 'Use another profile'},
    'removedContentPage': {'text': "What happened"},
    'checkOnAnotherDevice': {'text': "Check your notifications on another device"},
    'allowCookiesPage': {'content-desc': "Allow the use of cookies by Instagram?"},
    'configuringAdsPage': {'content-desc': "Choose if we process your data for ads"}
}

# table with all tasks, structure:
# [requirements (from patterns table)]: adbScript function
taskTable: dict[tuple[str], ADB_SCRIPT_CONTRACT] = {
    ('passwordTextField',): inputCredsPage,
    ('2faLabel',): fa2Page,
    ('saveLoginInfoPage',): saveLoginInfoPage,
    ('addInstagramAccountButton',): addInstagramAccount,
    ('logIntoAccountButton',): logIntoAccountButton,
    ('promoDialog',): promoDialogDispatcher,
    ('accessToContactsPage',): accessToContactsPage,
    ('disableLocationServices',): disableLocationServices,
    ('relevantAdsPage',): relevantAdsPage,
    ('useAnotherProfile',): useAnotherProfile,
    ('removedContentPage',): closeRemovedContentPage,
    ('checkOnAnotherDevice',): checkOnAnotherDevicePage,
    ('allowCookiesPage',): allowCookies,
    ('configuringAdsPage',): configuringAds
}



def checkDetectedPatterns(detectingResult: list[str], *patterns: *tuple[str]) -> bool:
    """
        Checks if all patterns were detected.
    """
    return all([pattern in detectingResult for pattern in patterns])


@adbScript
def loginScriptDetector(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, fa2Secret: str, screenDump: str) -> Optional[bool]:
    """
        Function to detect "task" which you need to complete.
        Using patters for pages elements.
        screenDump - another optimization level
    """

    # all found patterns
    detectingResult = []
    screenDump = adbAuto.screenDump if not screenDump else screenDump

    logger.debug(adb.serial + ' Searching for patterns...')

    for patternName, patternAttr in patterns.items():
        if adbAuto.getDumpElement(screenDump, patternAttr):
            detectingResult.append(patternName)

    logger.debug(adb.serial, f'Found {len(detectingResult)} patterns. Found: ', *detectingResult)

    for requirements, task in taskTable.items():
        if checkDetectedPatterns(detectingResult, *requirements):
            taskResult = task(adb, adbAuto, login, password, fa2Secret)
            # remove pattern if it was found and task is completed (don't let script work without any stops)
            for r in requirements: del patterns[r]
            return taskResult

    return None # if task not found


@adbScript
def loginScript(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, fa2Secret: str) -> bool:
    if adbAuto.getDumpElement(
        adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'}
    ):
        adbAuto.clickInRect(
            *adbAuto.getElementBounds(
                adbAuto.getDumpElement( adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'} )
            ), clickDuration=random.randint(2, 3)
        )

    # counter for "NotFound" detecting results (None)
    notFoundHistory = 0

    while True:
        try:
            lastCheckedScreenDump = adbAuto.screenDump
            detectionResult = loginScriptDetector(adb, adbAuto, login, password, fa2Secret, lastCheckedScreenDump)
            if detectionResult is None: notFoundHistory += 1
            if notFoundHistory >= 4: break

            # do not use this variable with detector, because dump may be changed after that
            screenDump = adbAuto.screenDump
            if any([
                adbAuto.getDumpElement( screenDump, {'content-desc': f'Confirm you\'re human to use your account, {login}'} ),
                adbAuto.getDumpElement( screenDump, {'text': "Confirm you're human"} )
            ]):
                logger.error(adb.serial, f'Cannot use account {login} without confirmation!')
                logoutAfterConfirmation(adb, adbAuto, login, password, fa2Secret)
                return False

            # updating screen dump after every iteration
            for _ in range(10):
                newDump = adbAuto.screenDump
                if newDump != lastCheckedScreenDump: break
                time.sleep(1)

        except Exception as e:
            logger.error(adb.serial, e)

    return True