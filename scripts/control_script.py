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
def parseAccounts(adb: AdbClient, adbAuto: AdbAutomatization, dump: str) -> list[str]:
    activeAccounts = []

    accountsSection: Optional[bs4.element.Tag] = adbAuto.getDumpElement(
        dump, {'resource-id': "com.instagram.android:id/recycler_view_container_id"}
    )

    if not accountsSection:
        logger.error(adb.serial, 'Cannot find accounts section. Aborting...')
        return []

    accountsSection = accountsSection.get('node', None)

    for accountSection in accountsSection.find_all('node'):
        innerNode: Optional[bs4.element.Tag] = accountSection.get('node')
        if not innerNode: continue

        testSection: Optional[bs4.element.Tag] = innerNode.get('node', None)
        if not testSection: continue

        activeAccount = testSection.get('content-desc')
        if activeAccount: activeAccounts.append(activeAccount)

    return activeAccounts


@adbScript
def parseActiveAccounts(adb: AdbClient, adbAuto: AdbAutomatization) -> list[str]:
    activeAccounts: list[str] = []

    if not adbAuto.getDumpElement(
        adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'}
    ):
        logger.error(adb.serial, 'Cannot find profile button. Aborting...')
        return []

    adbAuto.clickInRect(
        *adbAuto.getElementBounds(
            adbAuto.getDumpElement( adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/profile_tab'} )
        ), clickDuration=random.randint(2, 3)
    )

    adbAuto.waitForElement({'resource-id': 'com.instagram.android:id/recycler_view_container_id'})

    firstScreenDump = adbAuto.screenDump
    for acc in parseAccounts(adb, adbAuto, firstScreenDump): activeAccounts.append(acc)

    # swiping for some more new accounts
    for _ in range(2):
        adbAuto.swipeInRect(
        *adbAuto.getElementBounds(
                adbAuto.getDumpElement(
                    adbAuto.screenDump, {'resource-id': 'com.instagram.android:id/recycler_view_container_id'}
                )
            ), direction=False
        )

    secondScreenDump = adbAuto.screenDump
    if secondScreenDump != firstScreenDump:
        # parse it again
        for acc in parseAccounts(secondScreenDump): activeAccounts.append(acc)

    logger.info(adb.serial, 'Gotten active accounts: ' + str(len(activeAccounts)), '. Returning...')
    adb.tap(Dot(300, 300).make_random())

    return activeAccounts