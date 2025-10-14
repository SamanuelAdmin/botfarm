from datetime import datetime

from core.middleware import adbScript
from services.adb_manager import AdbClient
from services.adb_manager.adb_auto import AdbAutomatization



def simpleLog(adb: AdbClient, *logs):
    currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{currentTime}] {adb.serial} - ', *logs)


def openViaLink(adb: AdbClient, link: str) -> bool:
    return bool(adb.sendAdbCommand(
        f'am start -a android.intent.action.VIEW -d {link} com.instagram.android'
    ))

# def checkForAlertDialog(adb: AdbClient, adbAuto, link: str) -> bool:
#     # TRUE - EVERYTHING OK, FALSE - NOT OKAY
#     alertDialogSoup = adbAuto.getElementSoup(
#         adb.getScreenDump(),
#         elementAttrs={'resource-id': 'com.instagram.android:id/igds_alert_dialog_headline'}
#     )
#     promoDialogSoup = adbAuto.getElementSoup(
#         adb.getScreenDump(),
#         elementAttrs={'resource-id', 'com.instagram.android:id/igds_headline_headline'}
#     )
#
#     if alertDialogSoup:
#         adbAuto.clickOnElement(
#             client=adb,
#             elementAttrs={'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'}
#         )
#
#         if alertDialogSoup['text'] == "Your request is pending":
#             simpleLog(
#                 adb, 'ALERT! Account cannot follow other accounts!',
#                 f'Alert dialog: {alertDialogSoup}',
#                 f'Clients account: {link}',
#                 'Returning...'
#             ); return False
#
#     elif promoDialogSoup:
#         adbAuto.clickOnElement(
#             client=adb,
#             elementAttrs={'resource-id': 'com.instagram.android:id/igds_promo_dialog_action_button'}
#         )
#         simpleLog(adb, f'Activate [', promoDialogSoup['text'], ']')
#
#     return True

@adbScript
def likePost(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    simpleLog(adb, f'Opening post via link {link}')
    openViaLink(adb, link)


    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/row_feed_button_like'}
    )

    simpleLog(adb, 'Loaded. Leaving like...')
    adbAuto.clickInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement(
                adbAuto.screenDump,
                {'resource-id': 'com.instagram.android:id/row_feed_button_like'}
            )
        ),
    )

    simpleLog(adb, 'Done. Returning...')

    adbAuto.clickInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement(
                adbAuto.screenDump,
                {'resource-id': 'com.instagram.android:id/action_bar_button_back'}
            )
        ),
    )

    return True

# def returnViaReturnButton(adb : AdbClient, adbAuto: AdbAutomatization) -> bool:
#     simpleLog(adb, 'Returning...')
#     return adbAuto.clickOnElement(
#         client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_back'}
#     )
#
#
# def followAccount(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
#     simpleLog(adb, f'Opening profile via link {link}')
#     openViaLink(adb, link)
#
#     waitForDumpElement(
#         adb, adbAuto, elementAttrs={'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'}
#     )
#
#     # check if account is already followed
#     followButtonSoup = adbAuto.getElementSoup(
#         adb.getScreenDump(), elementAttrs={'resource-id': 'com.instagram.android:id/profile_header_follow_button'}
#     )
#
#     if followButtonSoup.node['text'] != 'Follow':
#         simpleLog(adb, 'Account is already following.')
#         returnViaReturnButton(adb, adbAuto)
#         return False
#
#
#     simpleLog(adb, 'Loaded. Leaving follower...')
#     adbAuto.clickOnElement(
#         client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'}
#     )
#
#     randomDelay(2, 3)
#     status = checkForAlertDialog(adb, adbAuto, link)
#
#     returnViaReturnButton(adb, adbAuto)
#
#     # checking again
#     if status:
#         randomDelay(1, 2)
#         status = checkForAlertDialog(adb, adbAuto, link)
#
#     return status


