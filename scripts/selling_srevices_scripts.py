from datetime import datetime

from core.middleware import adbScript
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization, PostActions


def simpleLog(adb: AdbClient, *logs):
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{currentTime}] {adb.serial} - ', *logs)


def openViaLink(adb: AdbClient, link: str) -> bool:
    return bool(adb.sendAdbCommand(
        f'am start -a android.intent.action.VIEW -d {link} com.instagram.android'
    ))


@adbScript
def checkForAlertDialog(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    # TRUE - EVERYTHING OK, FALSE - NOT OKAY
    alertDialogSoup = adbAuto.getDumpElement(
        adbAuto.screenDump,
        {'resource-id': 'com.instagram.android:id/igds_alert_dialog_headline'}
    )
    promoDialogSoup = adbAuto.getDumpElement(
        adbAuto.screenDump,
        {'resource-id': 'com.instagram.android:id/igds_headline_headline'}
    )

    if alertDialogSoup:
        adbAuto.waitForElement(
            {'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'},
            postActions=(PostActions.clickOnElement,)
        )

        if alertDialogSoup['text'] == "Your request is pending":
            simpleLog(
                adb, 'ALERT! Account cannot follow other accounts!',
                f'Alert dialog: {alertDialogSoup}',
                f'Clients account: {link}',
                'Returning...'
            ); return False

    elif promoDialogSoup:
        adbAuto.waitForElement(
            {'resource-id': 'com.instagram.android:id/igds_promo_dialog_action_button'},
            postActions=(PostActions.clickOnElement,)
        )

        simpleLog(adb, f'Activate [', promoDialogSoup['text'], ']')

    return True


@adbScript
def likePost(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    simpleLog(adb, f'Opening post via link {link}')
    openViaLink(adb, link)


    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/row_feed_button_like'},
        postActions=( PostActions.clickOnElement, )
    )

    simpleLog(adb, 'Loaded. Leaved like, returning...')

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_back'},
        postActions=( PostActions.clickOnElement, )
    )

    return True


@adbScript
def followAccount(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    simpleLog(adb, f'Opening profile via link {link}')
    openViaLink(adb, link)

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'},
        # postActions=( PostActions.clickOnElement, )
    )

    # check if account is already followed
    followButtonSoup = adbAuto.getDumpElement(
        adbAuto.screenDump,
        {'resource-id': 'com.instagram.android:id/profile_header_follow_button'}
    )

    if followButtonSoup.node['text'] != 'Follow':
        simpleLog(adb, 'Account is already following.')

        adbAuto.waitForElement(
            {'content-desc': "Back"},
            postActions=(PostActions.clickOnElement,)
        )
        return False


    simpleLog(adb, 'Loaded. Leaving follower...')
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'},
        postActions=( PostActions.clickOnElement, )
    )

    simpleLog(adb, 'Done. Returning...')
    adbAuto.randomDelay(2, 3)
    status = checkForAlertDialog(adb, adbAuto, link)

    adbAuto.waitForElement(
        {'content-desc': "Back"},
        postActions=(PostActions.clickOnElement,)
    )

    simpleLog(adb, 'Done.')

    # checking again
    if status:
        adbAuto.randomDelay(2, 3)
        status = checkForAlertDialog(adb, adbAuto, link)

    return True


