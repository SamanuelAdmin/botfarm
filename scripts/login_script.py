"""
    Script with "modules" architecture.
    Processing method:
    1) Starting...
    2) Detector - detect "task" which you need to complete
    3) Doing task...
    4) Returns to detector and checking if it's finished.
"""


import random
from typing import Optional

from core.logger import Logger
from core.middleware import adbScript
from core.middleware import ADB_SCRIPT_CONTRACT
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization, PostActions
from services.fa2 import get2FACode



@adbScript
def inputCredsPage(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, *args) -> bool:
    adbAuto.log(adb.serial, ' Inputting username...')
    adbAuto.waitForElement(
        { 'class': "android.widget.EditText" },
        postActions=( PostActions.clickOnElement, )
    )
    adb.fastText(login)
    adbAuto.log(adb.serial + ' Username entered.')

    adbAuto.log(adb.serial + ' Inputting password...')
    adbAuto.waitForElement(
        { 'content-desc': "Password,", 'class': "android.widget.EditText" },
        postActions=( PostActions.clickOnElement, )
    )
    adb.fastText(password)
    adbAuto.log(adb.serial + ' Password entered. Pressing Log in button...')

    adbAuto.waitForElement(
        { 'content-desc': "Log in", 'class': "android.widget.Button" },
        postActions=( PostActions.clickOnElement, )
    )

    return True


@adbScript
def fa2Page(adb: AdbClient, adbAuto: AdbAutomatization, login: str, password: str, fa2Secret) -> bool:
    adbAuto.log(adb.serial + ' Getting 2fa code...')
    FA2Code = get2FACode(fa2Secret)

    adbAuto.log(adb.serial + ' Entering 2FA code...')
    adbAuto.waitForElement(
        {'class': "android.widget.EditText"},
        postActions=( PostActions.clickOnElement, )
    )
    adb.fastText(FA2Code)

    adbAuto.log(adb.serial + ' Confirming 2fa code.')
    adbAuto.waitForElement(
        {'content-desc': "Continue"},
        postActions=( PostActions.clickOnElement, )
    )

    return True



# patterns for each element. required in modules architecture
# element_name : element_attrs
patterns: dict[str, dict[str, str]] = {
    'usernameTextField': { 'index': "0", 'class': "android.widget.EditText" },
    'passwordTextField': { 'content-desc': "Password,", 'class': "android.widget.EditText" },
    '2faLabel': {'text': "Enter the 6-digit code for this account from the two-factor authentication app you set up (such as Duo Mobile or Google Authenticator)."},
}

# table with all tasks, structure:
# [requirements (from patterns table)]: adbScript function
taskTable: dict[tuple[str], ADB_SCRIPT_CONTRACT] = {
    ('passwordTextField',): inputCredsPage
}



def checkDetectedPatterns(detectingResult: list[str], *patterns: *tuple[str]) -> bool:
    """
        Checks if all patterns were detected.
    """
    return all([pattern in detectingResult for pattern in patterns])


@adbScript
def loginScriptDetector(adb: AdbClient, adbAuto: AdbAutomatization, login, password, fa2Secret) -> Optional[bool]:
    """
        Function to detect "task" which you need to complete.
        Using patters for pages elements.
    """

    # all found patterns
    detectingResult = []
    screenDump = adb.getScreenDump()

    adbAuto.log(adb.serial + ' Searching for patterns...')

    for patternName, patternAttr in patterns.items():
        if adbAuto.getDumpElement(screenDump, patternAttr):
            detectingResult.append(patternName)

    adbAuto.log(adb.serial, f' Found {len(detectingResult)} patterns. Found: ', *detectingResult)

    for requirements, task in taskTable.items():
        if checkDetectedPatterns(detectingResult, *requirements):
            return task(adb, adbAuto, login, password, fa2Secret)

    return None # if task not found


@adbScript
def loginScript(adb: AdbClient, adbAuto: AdbAutomatization, login, password, fa2Secret):
    try:
        for i in range(2):
            loginScriptDetector(adb, adbAuto, login, password, fa2Secret)
    except Exception as e: print(e)

    # go to profile page
    # adbAuto.clickInRect(
    #     adbAuto.getElementBounds(
    #         adbAuto.getDumpElement( adbAuto.screenDump, {'content-desc': 'Profile'} )
    #     ), clickDuration=random.choice(range(2500, 4000))
    # )
    #
    # adbAuto.log(adb.serial, 'Opened accounts menu.')
    #
    # swipeUntilFindElement(
    #     adb,
    #     dumpAttrs={'content-desc': "Add Instagram account"},
    #     adbAuto=adbAuto
    # )
    # simpleLog(adb, 'Adding new account...')
    # adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Add Instagram account"})
    #
    # simpleLog(adb, 'Logging into exiting account...')
    # waitForDumpElement(adb, adbAuto, elementAttrs={'content-desc': "Log into existing account"})
    # adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Log into existing account"})
    #
    # simpleLog(adb, 'Using another profile...')
    # waitForDumpElement(adb, adbAuto, elementAttrs={'content-desc': "Use another profile"})
    # adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Use another profile"})
    #
    # simpleLog(adb, 'Waiting for login page...')
    # waitForDumpElement(adb, adbAuto, elementAttrs={'class': "android.widget.EditText"})
    #
    # loginPageDump = adb.getScreenDump()
    # usernameSoup = adbAuto.getElementSoup(
    #     loginPageDump, elementAttrs={'class': "android.widget.EditText"}
    # )
    # oldUsername = usernameSoup['text']
    #
    # if oldUsername: # deleting old username
    #     simpleLog(adb, f'Gotten old username: {oldUsername} with length: {len(oldUsername)}. Deleting...')
    #     adbAuto.clickOnElement( client=adb, elementAttrs={'class': "android.widget.EditText"} )
    #
    #     simpleLog(adb, 'Deleting old username...')
    #     adb.deleteText(length=len(oldUsername) + random.randint(2, 5))
    #
    #
    # simpleLog(adb, 'Inputting new username...')
    # adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'class': "android.widget.EditText"}
    # )
    # adb.fastText(login)
    #
    # simpleLog(adb, 'Done. Inputting password...')
    # adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'password': "true"}
    # )
    # adb.fastText(password)
    #
    # simpleLog(adb, 'Done. Logging in...')
    # adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'text': "Log in"}
    # )
    #
    # waitForDumpElement(
    #     adb, adbAuto,
    #     elementAttrs={'text': "Enter the 6-digit code for this account from the two-factor authentication app you set up (such as Duo Mobile or Google Authenticator)."}
    # )
    # simpleLog(adb, 'Done. Getting 2FA code...')
    #
    # FA2Code = get2FACode(fa2Secret)
    # simpleLog(adb, 'Done. Entering 2FA code...')
    # adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'class': "android.widget.EditText"}
    # )
    # adb.fastText(FA2Code)
    #
    # simpleLog(adb, 'Done. Confirming...')
    # adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Continue"})
    #
    # simpleLog(adb, 'Saving login info...')
    # waitForDumpElement(
    #     adb, adbAuto, elementAttrs={'content-desc': "Save your login info?"}
    # )
    # adbAuto.clickOnElement(client=adb, elementAttrs={'text': "Save"})
    #
    # simpleLog(adb, 'Finishing...')
    # randomDelay(3, 7)
    # if adbAuto.getElementSoup(
    #     adb.getScreenDump(), elementAttrs={'text': "Finish setting up your account"}
    # ): adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'resource-id': "com.instagram.android:id/igds_promo_dialog_secondary_button"}
    # )
    #
    # randomDelay(1, 3)
    # if adbAuto.getElementSoup(
    #     adb.getScreenDump(), elementAttrs={'text': 'Allow access to contacts to find people to follow'}
    # ): adbAuto.clickOnElement(
    #     client=adb, elementAttrs={'content-desc': 'Skip'}
    # )
    #
    # simpleLog(adb, 'Done')
    # return True