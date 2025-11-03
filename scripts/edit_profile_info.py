import time

from core.logger import Logger
from core.middleware.decorators import adbScript
from core.hardware import AdbClient
from core.hardware import AdbAutomatization, PostActions

logger = Logger()


@adbScript
def openProfileEditor(adb: AdbClient, adbAuto: AdbAutomatization) -> bool:
    return bool(adb.sendAdbCommand(
        f'am start -a android.intent.action.VIEW -d "instagram://editprofile"'
    ))


@adbScript
def editProfileImage(adb: AdbClient, adbAuto: AdbAutomatization, pathToImage: str) -> bool:
    try:
        newImagePath = '/sdcard/DCIM/profile.jpg'

        # pushing image to device
        logger.debug(adb.serial, f'Pushing image to device... Using path: {pathToImage}')
        adb.sendAdbCommand( f'push "{pathToImage}" "{newImagePath}"' )
        adb.sendAdbCommand(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{newImagePath}')
        logger.debug(adb.serial, f'Done.')

        openProfileEditor(adb, adbAuto)
        logger.debug(adb.serial, 'Opened edit profile page')

        adbAuto.waitForElement(
            {'text': "Change profile picture"},
            postActions=(PostActions.clickOnElement,)
        )
        logger.debug(adb.serial, 'Changing profile picture...')

        adbAuto.waitForElement(
            {'resource-id': "com.instagram.android:id/row_label"},
            postActions=(PostActions.clickOnElement,)
        )
        logger.debug(adb.serial, 'Taking image from gallery...')

        adbAuto.waitForElement(
            {'resource-id': "com.instagram.android:id/next_button_textview"},
            postActions=(PostActions.clickOnElement,)
        )

        logger.debug(adb.serial, 'Done. Returning...')

        time.sleep(5)
        return True

    except Exception as e:
        logger.error(str(e))
        return False


@adbScript
def saveChanges(adb: AdbClient, adbAuto: AdbAutomatization) -> bool:
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_action'},
        postActions=(PostActions.clickOnElement,)
    )
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'},
        postActions=(PostActions.clickOnElement,)
    )
    return True


def getEditFieldData(adb: AdbClient, adbAuto: AdbAutomatization, attrs: dict[str, str]) -> str:
    field = adbAuto.getDumpElement( adbAuto.screenDump, attrs )
    adbAuto.clickInRect(*adbAuto.getElementBounds(field))
    return field.get('text')


@adbScript
def setNewName(adb: AdbClient, adbAuto: AdbAutomatization, name: str= "") -> bool:
    logger.debug(adb.serial, 'Clicking to edit name...')
    adbAuto.waitForElement({'resource-id': "com.instagram.android:id/full_name"}, )
    nameBounds = adbAuto.getElementBounds(
        adbAuto.getDumpElement(adbAuto.screenDump, {'resource-id': "com.instagram.android:id/full_name"}).node
    )

    for _ in range(2):  # click 5 times
        adbAuto.clickInRect(*nameBounds)

    logger.debug(adb.serial, 'Waiting for edit name page...')
    adbAuto.waitForElement({'resource-id': "com.instagram.android:id/full_name_change_limiting_textview"})

    logger.debug(adb.serial, 'Page is loaded, getting old name to delete...')
    oldName = getEditFieldData(adb, adbAuto, {'class': "android.widget.EditText", 'resource-id': ""})

    if oldName:
        logger.debug(adb.serial, f'Old name is {oldName}, length is {len(oldName)}. Deleting...')
        adb.deleteText(length=int(len(oldName) * 1.1))

    logger.debug(adb.serial, 'Inputting new name...')
    adb.fastText(name)

    logger.debug(adb.serial, 'Done, saving new name...')
    saveChanges(adb, adbAuto)

    return True


@adbScript
def setNewUsername(adb: AdbClient, adbAuto: AdbAutomatization, username: str= "") -> bool:
    logger.debug(adb.serial, 'Clicking to edit username...')
    adbAuto.waitForElement({'resource-id': "com.instagram.android:id/username"}, )
    usernameBounds = adbAuto.getElementBounds(
        adbAuto.getDumpElement(adbAuto.screenDump, {'resource-id': "com.instagram.android:id/username"}).node
    )

    for _ in range(2):  # click 5 times
        adbAuto.clickInRect(*usernameBounds)

    logger.debug(adb.serial, 'Page is loaded, getting old username to delete...')
    oldUsername = getEditFieldData(adb, adbAuto, {'class': "android.widget.EditText", 'resource-id': ""})

    if oldUsername:
        logger.debug(adb.serial, f'Old username is {oldUsername}, length is {len(oldUsername)}. Deleting...')
        adb.deleteText(length=int(len(oldUsername) * 1.1))

    logger.debug(adb, 'Inputting new username...')
    adb.fastText(username)

    logger.debug(adb, 'Done, saving new username...')
    # saveChanges(hardware, adbAuto)
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_action'},
        postActions=(PostActions.clickOnElement,)
    )

    return True


@adbScript
def setNewBio(adb: AdbClient, adbAuto: AdbAutomatization, bio: str= "") -> bool:
    logger.debug(adb.serial, 'Clicking to edit bio...')
    adbAuto.waitForElement({'resource-id': "com.instagram.android:id/bio"}, )
    bioBounds = adbAuto.getElementBounds(
        adbAuto.getDumpElement(adbAuto.screenDump, {'resource-id': "com.instagram.android:id/bio"}).node
    )

    adbAuto.clickInRect(*bioBounds)

    logger.debug(adb.serial, 'Page is loaded, getting old bio to delete...')
    oldBio = getEditFieldData(adb, adbAuto, {'class': "android.widget.EditText", 'resource-id': ""})

    if oldBio:
        adb.deleteText(length=len(oldBio))

    logger.debug(adb.serial, 'Inputting new bio...')
    adb.bufferProcessor.copy(bio)
    adb.bufferProcessor.paste()

    logger.debug(adb.serial, 'Done, saving new bio...')
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_action'},
        postActions=(PostActions.clickOnElement,)
    )

    return True


def editProfileInfoScript(adb: AdbClient, adbAuto: AdbAutomatization, name: str= "", username: str= "", bio: str= "", pathToImage: str=""):
    # go to profile page
    openProfileEditor(adb, adbAuto)
    logger.debug(adb.serial, 'Opened edit profile page.')


    if name: setNewName(adb, adbAuto, name)
    if username: setNewUsername(adb, adbAuto, username)
    if bio: setNewBio(adb, adbAuto, bio)
    if pathToImage: editProfileImage(adb, adbAuto, pathToImage)


    logger.debug(adb.serial, 'Done. Returning...')
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_back'},
        postActions=( PostActions.clickOnElement, )
    )
    return True