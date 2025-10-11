from services.fa2 import get2FACode
from scripts.OLD.scripts_builder import *



def loginScriptV2(adb: AdbClient, adbAuto: AdbAutomatization, login, password, fa2Secret):
    # go to profile page
    adbAuto.clickOnElement(
        client=adb, elementAttrs={'content-desc': 'Profile'},
        longClick=True, longClickDelay=random.choice(range(2, 4))
    )
    simpleLog(adb, 'Opened accounts menu.')

    swipeUntilFindElement(
        adb,
        dumpAttrs={'content-desc': "Add Instagram account"},
        adbAuto=adbAuto
    )
    simpleLog(adb, 'Adding new account...')
    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Add Instagram account"})

    simpleLog(adb, 'Logging into exiting account...')
    waitForDumpElement(adb, adbAuto, elementAttrs={'content-desc': "Log into existing account"})
    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Log into existing account"})

    simpleLog(adb, 'Using another profile...')
    waitForDumpElement(adb, adbAuto, elementAttrs={'content-desc': "Use another profile"})
    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Use another profile"})

    simpleLog(adb, 'Waiting for login page...')
    waitForDumpElement(adb, adbAuto, elementAttrs={'class': "android.widget.EditText"})

    loginPageDump = adb.getScreenDump()
    usernameSoup = adbAuto.getElementSoup(
        loginPageDump, elementAttrs={'class': "android.widget.EditText"}
    )
    oldUsername = usernameSoup['text']

    if oldUsername: # deleting old username
        simpleLog(adb, f'Gotten old username: {oldUsername} with length: {len(oldUsername)}. Deleting...')
        adbAuto.clickOnElement( client=adb, elementAttrs={'class': "android.widget.EditText"} )

        simpleLog(adb, 'Deleting old username...')
        adb.deleteText(length=len(oldUsername) + random.randint(2, 5))


    simpleLog(adb, 'Inputting new username...')
    adbAuto.clickOnElement(
        client=adb, elementAttrs={'class': "android.widget.EditText"}
    )
    adb.fastText(login)

    simpleLog(adb, 'Done. Inputting password...')
    adbAuto.clickOnElement(
        client=adb, elementAttrs={'password': "true"}
    )
    adb.fastText(password)

    simpleLog(adb, 'Done. Logging in...')
    adbAuto.clickOnElement(
        client=adb, elementAttrs={'text': "Log in"}
    )

    waitForDumpElement(
        adb, adbAuto,
        elementAttrs={'text': "Enter the 6-digit code for this account from the two-factor authentication app you set up (such as Duo Mobile or Google Authenticator)."}
    )
    simpleLog(adb, 'Done. Getting 2FA code...')

    FA2Code = get2FACode(fa2Secret)
    simpleLog(adb, 'Done. Entering 2FA code...')
    adbAuto.clickOnElement(
        client=adb, elementAttrs={'class': "android.widget.EditText"}
    )
    adb.fastText(FA2Code)

    simpleLog(adb, 'Done. Confirming...')
    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Continue"})

    simpleLog(adb, 'Saving login info...')
    waitForDumpElement(
        adb, adbAuto, elementAttrs={'content-desc': "Save your login info?"}
    )
    adbAuto.clickOnElement(client=adb, elementAttrs={'text': "Save"})

    simpleLog(adb, 'Finishing...')
    randomDelay(3, 7)
    if adbAuto.getElementSoup(
        adb.getScreenDump(), elementAttrs={'text': "Finish setting up your account"}
    ): adbAuto.clickOnElement(
        client=adb, elementAttrs={'resource-id': "com.instagram.android:id/igds_promo_dialog_secondary_button"}
    )

    randomDelay(1, 3)
    if adbAuto.getElementSoup(
        adb.getScreenDump(), elementAttrs={'text': 'Allow access to contacts to find people to follow'}
    ): adbAuto.clickOnElement(
        client=adb, elementAttrs={'content-desc': 'Skip'}
    )

    simpleLog(adb, 'Done')
    return True