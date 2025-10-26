"""

    Scripts for all controlling operations like changing account,
    parsing active accounts list etc.

"""
import random
from typing import Optional
import bs4

from core.logger import Logger
from core.middleware import adbScript
from services.adb_manager import AdbClient, Dot
from services.adb_manager.adb_auto import AdbAutomatization


logger = Logger(setDatetime=False)


@adbScript
def _scrollDownAccounts(adb: AdbClient, adbAuto: AdbAutomatization) -> None:
    for _ in range(2):
        adbAuto.swipeInRect(
            *adbAuto.getElementBounds(
                adbAuto.getDumpElement(
                    adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/recycler_view_container_id'}
                )
            ), direction=False
        )


@adbScript
def _hideAccountsList(adb: AdbClient, adbAuto: AdbAutomatization) -> None:
    adbAuto.swipeInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement(adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/recycler_view_container_id'})
        )
    )


@adbScript
def _checkForProfileButton(adb: AdbClient, adbAuto: AdbAutomatization) -> bool:
    if adbAuto.getDumpElement(
            adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'}
    ): return True

    logger.error(adb.serial, 'Cannot find profile button. Aborting...')
    return False


@adbScript
def _openAccountsList(adb: AdbClient, adbAuto: AdbAutomatization) -> None:
    adbAuto.clickInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement( adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'} )
        ), clickDuration=random.randint(2, 3)
    )

    adbAuto.waitForElement({'resource-id': 'com.instagram.android:id/recycler_view_container_id'})


@adbScript
def _parseAccounts(adb: AdbClient, adbAuto: AdbAutomatization, dump: str) -> list[str]:
    activeAccounts = []

    accountsSection: Optional[bs4.element.Tag] = adbAuto.getDumpElement(
        dump, {'resource-id': "com.instagram.android:id/recycler_view_container_id"}
    )
    accountsSection = accountsSection.node if accountsSection else None

    if not accountsSection:
        logger.error(adb.serial, 'Cannot find accounts section. Aborting...')
        return []


    for accountSection in accountsSection.find_all('node'):
        try:
            activeAccount = accountSection.node.node \
                .find(attrs={'index': "1"}).get('text')
            if activeAccount and ' ' not in activeAccount:
                activeAccounts.append(activeAccount)
        except (AttributeError, ValueError): continue

    return activeAccounts


@adbScript
def parseActiveAccounts(adb: AdbClient, adbAuto: AdbAutomatization) -> list[str]:
    activeAccounts: list[str] = []

    if not _checkForProfileButton(adb, adbAuto): return []
    _openAccountsList(adb, adbAuto)

    firstScreenDump = adbAuto.screenDump
    for acc in _parseAccounts(adb, adbAuto, firstScreenDump): activeAccounts.append(acc)

    # swiping for some more new accounts
    for _ in range(2): _scrollDownAccounts(adb, adbAuto)

    secondScreenDump = adbAuto.screenDump
    if secondScreenDump != firstScreenDump:
        # parse it again, and remove duplicates
        activeAccounts = list({*activeAccounts, _parseAccounts(adb, adbAuto, secondScreenDump)})

    logger.info(adb.serial, 'Gotten active accounts: ' + str(len(activeAccounts)), '. Returning...')
    for _ in range(2): _hideAccountsList(adb, adbAuto)
    return activeAccounts



@adbScript
def changeAccount(adb: AdbClient, adbAuto: AdbAutomatization, username: str) -> bool:
    try:
        if not _checkForProfileButton(adb, adbAuto): return False
        _openAccountsList(adb, adbAuto)

        def _chooseAccount(adb: AdbClient, adbAuto: AdbAutomatization, usernameButton: bs4.element.Tag) -> bool:
            adbAuto.clickInRect( *adbAuto.getElementBounds(usernameButton) )

            if adbAuto.getDumpElement(adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/recycler_view_container_id'}):
                _hideAccountsList(adb, adbAuto)


        # checking for account
        firstScreenDump = adbAuto.screenDump
        usernameButton = adbAuto.getDumpElement(firstScreenDump, {'text': username})
        if usernameButton:
            _chooseAccount(adb, adbAuto, usernameButton)
            return True

        for _ in range(2): _scrollDownAccounts(adb, adbAuto)

        secondScreenDump = adbAuto.screenDump
        if secondScreenDump == firstScreenDump:
            _hideAccountsList(adb, adbAuto)
            return False


        usernameButton = adbAuto.getDumpElement(secondScreenDump, {'text': username})
        if usernameButton:
            _chooseAccount(adb, adbAuto, usernameButton)
            return True

        _hideAccountsList(adb, adbAuto)
        return False
    except Exception as e:
        print(e)
        return False