from core.logger import Logger
from core.middleware.decorators import adbScript
from core.hardware import AdbClient
from core.hardware import AdbAutomatization, PostActions


logger = Logger(setDatetime=False)


@adbScript
def openViaLink(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    return bool(adb.sendAdbCommand(
        f'am start -a android.intent.action.VIEW -d {link} com.instagram.android'
    ))


@adbScript
def checkForAlertDialog(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    # TRUE - EVERYTHING OK, FALSE - NOT OKAY
    returnStatus = True

    alertDialogSoup = adbAuto.getDumpElement(
        adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/igds_alert_dialog_headline'}
    )

    if alertDialogSoup:
        adbAuto.waitForElement(
            {'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'},
            postActions=(PostActions.clickOnElement,)
        )

        if alertDialogSoup['text'] == "Your request is pending":
            logger.error(
                adb.serial,
                'ALERT! Account cannot follow other accounts!',
                f'Alert dialog: {alertDialogSoup}',
                f'Clients account: {link}',
                'Returning...'
            )
            returnStatus = False

    promoDialogSoup = adbAuto.getDumpElement(
        adbAuto.screenDump,{'resource-id': 'com.instagram.android:id/igds_headline_headline'}
    )

    if promoDialogSoup:
        adbAuto.waitForElement(
            {'resource-id': 'com.instagram.android:id/igds_promo_dialog_action_button'},
            postActions=(PostActions.clickOnElement,)
        )

        logger.info(adb.serial, f'Activate [', promoDialogSoup['text'], ']')

    return returnStatus


@adbScript
def likePost(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    logger.debug(adb.serial, f'Opening post via link {link}')
    openViaLink(adb, adbAuto, link)


    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/row_feed_button_like'},
        postActions=( PostActions.clickOnElement, )
    )

    logger.info(adb.serial, 'Loaded. Leaved like, returning...')

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/action_bar_button_back'},
        postActions=( PostActions.clickOnElement, )
    )

    return True


@adbScript
def followAccount(adb: AdbClient, adbAuto: AdbAutomatization, link: str) -> bool:
    logger.debug(adb.serial, f'Opening profile via link {link}')
    openViaLink(adb, adbAuto, link)

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'},
        # postActions=( PostActions.clickOnElement, )
    )

    # check if account is already followed
    followButtonSoup = adbAuto.getDumpElement(
        adbAuto.screenDump,
        {'resource-id': 'com.instagram.android:id/profile_header_follow_button'}
    )

    if followButtonSoup['text'] != 'Follow':
        logger.warning(adb.serial, 'Account is already following.')

        adbAuto.waitForElement(
            {'content-desc': "Back"},
            postActions=(PostActions.clickOnElement,)
        )
        return False


    logger.info(adb.serial, 'Loaded. Leaving follower...')
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/profile_header_user_action_follow_button'},
        postActions=( PostActions.clickOnElement, )
    )

    logger.info(adb.serial, 'Done. Returning...')
    adbAuto.randomDelay(2, 3)
    status = checkForAlertDialog(adb, adbAuto, link)

    adbAuto.waitForElement(
        {'content-desc': "Back"},
        postActions=(PostActions.clickOnElement,)
    )

    logger.info(adb.serial, 'Done.')

    # checking again
    if status:
        adbAuto.randomDelay(2, 3)
        status = checkForAlertDialog(adb, adbAuto, link)

    return status



@adbScript
def commentPost(adb: AdbClient, adbAuto: AdbAutomatization, link: str, comment: str) -> bool:
    logger.debug(adb.serial, f'Opening profile via link {link}')
    openViaLink(adb, adbAuto, link)

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/row_feed_button_comment'},
        postActions=( PostActions.clickOnElement, )
    )

    logger.debug(adb.serial, 'Loaded. Leaving comment...')
    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/layout_comment_thread_edittext'},
        postActions=( PostActions.clickOnElement, )
    )
    # hardware.fastText(comment)
    adb.bufferProcessor.copy(comment)
    adb.bufferProcessor.paste()

    adbAuto.waitForElement(
        {'resource-id': 'com.instagram.android:id/layout_comment_thread_post_button_icon'},
        postActions=( PostActions.clickOnElement, )
    )

    adbAuto.swipeInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement(
                adbAuto.screenDump, {'class': "androidx.recyclerview.widget.RecyclerView"}
            )
        )
    )

    logger.debug(adb.serial, 'Comment leaved. Returning...')

    adbAuto.waitForElement(
        {'content-desc': "Back"},
        postActions=(PostActions.clickOnElement,)
    )

    return True