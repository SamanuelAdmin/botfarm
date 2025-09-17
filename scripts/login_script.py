import os

from services.adb_manager import AdbManager, Dot, AdbClient
from services.ui_recognizer import Recognizer
from services.insta_api.fa2 import get2FACode
from adb_auto import AdbAutoManager
from scripts.scripts_builder import *


def loginScript(adb: AdbClient, adbAuto: AdbAutoManager, login, password, fa2Secret) -> bool:
    recognizer = Recognizer(dataPath=os.path.join(os.getcwd(), 'services', 'ui_recognizer'))

    # go to account page
    goToProfilePage(adb, adbAuto)
    simpleLog(adb, 'Opened profile page')

    randomDelay(1, 1.1, 1.2, 1.3)
    clickViaTemplate(adb, recognizer, 'optionsButton')
    simpleLog(adb, 'Opened options list')
    randomDelay(1, 1.1, 1.2, 1.3)

    simpleLog(adb, 'Opening settings...')
    clickViaScreenText(adb, recognizer, 'settings')

    # IN SETTINGS PAGE
    randomDelay(1, 1.1, 1.2, 1.3)
    swipeUntilFindElement(adb, recognizer, text='add')

    if not clickViaScreenText(adb, recognizer, 'add'):
        raise Exception('Cannot find "ADD ACCOUNT" button')

    # simpleLog(adb, 'Opened account manager by "switch account" button')

    # simpleLog(adb, 'Searching for "add account" button')
    # randomDelay(1, 1.1, 1.2, 1.3)
    # swipeUntilFindElement(adb, recognizer, templateName='addAccountButton')
    # simpleLog(adb, 'Adding account... Clicking on "add account" button...')

    # if not clickViaTemplate(adb, recognizer, 'addAccountButton'):
    #     raise Exception('Cannot find "ADD ACCOUNT" button')

    # LOG INTO OR CREATE NEW ACCOUNT FIELD
    simpleLog(adb, 'Waiting for "Add account" field')
    waitForDumpElement(adb, adbAuto, {'content-desc': 'Log into existing account'})
    adbAuto.clickOnElement({'content-desc': 'Log into existing account'}, client=adb, randomizK=0.2)
    simpleLog(adb, 'Logging into existing account...')

    # HERE CAN BE "SWITCH ACCOUNT" PAGE
    randomDelay(3, 5)
    if checkTextOnScreen(adb, recognizer, 'switch'):
        clickViaScreenText(adb, recognizer, 'switch')

    # LOGING PAGE
    waitForDumpElement(adb, adbAuto, {'content-desc': 'Log in'})
    simpleLog(adb, 'Login page loaded. Entering login to the login field...')
    adbAuto.clickOnElement({'class': 'android.widget.MultiAutoCompleteTextView'}, client=adb)
    adb.fastText(login)

    simpleLog(adb, 'Done. Entering password to the password field...')
    adbAuto.clickOnElement({'password': 'true'}, client=adb)
    adb.fastText(password)

    simpleLog(adb, 'Done. Pressing "log in" button')
    adbAuto.clickOnElement({'content-desc': 'Log in'}, client=adb)

    # 2FA FIELD
    waitForDumpElement(adb, adbAuto, {'text': '_ _ _  _ _ _'})
    # press "trust this device" square
    simpleLog(adb, '2FA page loaded. Clicking on button "Trust this device"...')
    adbAuto.clickOnElement(client=adb, elementAttrs={'index': "9"})
    randomDelay(0.1)

    simpleLog(adb, 'Entering 2FA code...')
    adbAuto.clickOnElement(client=adb, elementAttrs={'text': '_ _ _  _ _ _'})
    fa2Code = get2FACode(fa2Secret)
    simpleLog(adb, 'Current 2FA code: ', fa2Code)
    adb.fastText(fa2Code)

    simpleLog(adb, 'Done. Confirming 2FA...')
    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Confirm"})


    # waiting for another actions
    randomDelay(10, 15)

    # checking for extra security step
    if checkTextOnScreen(adb, recognizer, 'extra security step is required'):
        # EXTRA SECURITY STEP
        simpleLog(adb, 'Security step is required')
        adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Continue"})

        # also can be
        randomDelay(10)
        if adbAuto.findElement(dump=adb.getScreenDump(), elementAttrs={'text': "Confirm you're human to use your account, ms.mark20747"}):
            simpleLog(adb, 'Confirming thats Im a human to use your account ', login, '. Swiping to the "Continue" button...')
            swipeUntilFindElement(adb, recognizer, dumpAttrs={'text': "Continue"})

            simpleLog(adb, 'Pressing continue...')
            if not adbAuto.clickOnElement(client=adb, elementAttrs={'text': "Continue"}):
                raise Exception('Cannot find "CONTINUE" button')

            print('Need to solve captcha...')
            input('PRESS ENTER TO CONTINUE')

        # waiting until page loaded
        waitForDumpElement(adb, adbAuto, {'text': "We Detected An Unusual Login Attempt"})
        simpleLog(adb, 'Security page loaded. Clicking on "This Was Me" button...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'text': "This Was Me"})

        randomDelay(7, 10)
        simpleLog(adb, "Done.")

    if adbAuto.findElement(dump=adb.getScreenDump(), elementAttrs={'resource-id': "new_password1"}):
        password += '1'
        simpleLog(adb, 'Changing password with security recomendations...\n   NEW PASSWORD: ', password, '\nEntering new password...')

        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': "new_password1"})
        adb.fastText(password)
        simpleLog(adb, 'Done. Confirming new password...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': "new_password2"})
        adb.fastText(password)

        simpleLog(adb, 'Done. Clicking "NEXT" button...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'text': "Next"})

        randomDelay(7, 10)
        if checkTextOnScreen(adb, recognizer, 'switch'):
            if not clickViaScreenText(adb, recognizer, 'switch'):
                raise Exception('Cannot switch to another account')

        simpleLog(adb, 'Account switched to ', login, '. Waiting for relogin page...')
        randomDelay(4, 7)
        waitForDumpElement(adb, adbAuto, {'password': 'true'}, iter=30)

        simpleLog(adb, 'Entering new password in login page ', login)
        adbAuto.clickOnElement(client=adb, elementAttrs={'password': "true"})
        adb.fastText(password + '1')

        simpleLog(adb, 'Done. Pressing "log in" button...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Log in"})

        randomDelay(4, 7)


    # MAYBE HERE WILL ALSO BE 2FA PAGE
    if adbAuto.findElement(dump=adb.getScreenDump(), elementAttrs={'text': "_ _ _  _ _ _"}):
        simpleLog(adb, 'Entering 2FA code...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'text': '_ _ _  _ _ _'})
        fa2Code = get2FACode(fa2Secret)
        simpleLog(adb, 'Current 2FA code: ', fa2Code)
        adb.fastText(fa2Code)
        simpleLog(adb, 'Done. Confirming 2FA...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Confirm"})

        randomDelay(3, 5)

    # IF WE NEED TO SAVE ACCOUNT INFO
    if checkTextOnScreen(adb, recognizer, 'save'):
        simpleLog(adb, 'Saving your login info...')

        if not clickViaTemplate(adb, recognizer, 'saveButton'):
            raise Exception('Cannot save your login info')


    return True