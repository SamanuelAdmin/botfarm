from scripts.OLD.scripts_builder import *




def waitForEditPage(adb, adbAuto):
    waitForDumpElement(
        adb, adbAuto,
        {
            'resource-id': "com.instagram.android:id/profile_pic_imageview"
        }
    )


def editProfileImage(adb: AdbClient, adbAuto: AdbAutomatization, pathToImage: str) -> bool:
    newImagePath = '/sdcard/DCIM/Camera/profile.jpg'

    # pushing image to device
    simpleLog(adb, f'Pushing image to device... Using path: {pathToImage}')
    adb.sendAdbCommand( f'push "{pathToImage}" "{newImagePath}"' )
    adb.sendAdbCommand(f'am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{newImagePath}')
    simpleLog(adb, f'Done.')

    goToProfilePage(adb, adbAuto)
    simpleLog(adb, 'Opened profile page')

    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Edit profile"})
    simpleLog(adb, 'Opened edit profile page')

    waitForDumpElement(adb, adbAuto, elementAttrs={'text': "Change profile picture"})
    adbAuto.clickOnElement(client=adb, elementAttrs={'text': "Change profile picture"})
    simpleLog(adb, 'Changing profile picture...')

    waitForDumpElement(adb, adbAuto, elementAttrs={'resource-id': "com.instagram.android:id/row_label"})
    adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': "com.instagram.android:id/row_label"})
    simpleLog(adb, 'Taking image from gallery...')

    waitForDumpElement(adb, adbAuto, elementAttrs={'resource-id': "com.instagram.android:id/next_button_textview"})
    randomDelay(1.1, 1.2, 1.3, 1.4, 1.5, 1.6)
    adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': "com.instagram.android:id/next_button_textview"})
    simpleLog(adb, 'Done. Returning...')

    if adbAuto.getElementSoup(
        adb.getScreenDump(), elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_back'}
    ): adbAuto.clickOnElement(
        client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_back'}
    )

    return True


def editProfileInfoScript(adb: AdbClient, adbAuto: AdbAutomatization, name: str= "", username: str= "", bio: str= ""):
    # go to profile page
    goToProfilePage(adb, adbAuto)
    simpleLog(adb, 'Opened profile page')

    adbAuto.clickOnElement(client=adb, elementAttrs={'content-desc': "Edit profile"})
    simpleLog(adb, 'Opened edit profile page')

    randomDelay(1, 1.1, 1.2, 1.3, 1.4)

    if name:
        waitForEditPage(adb, adbAuto)
        simpleLog(adb, 'Clicking to edit name...')
        adbAuto.clickOnElement(
            client=adb,  elementAttrs={
                'text': "Name",
            }, randomizK=0.2, yCorrector=70
        )

        simpleLog(adb, 'Waiting for edit name page...')
        waitForDumpElement(adb, adbAuto, elementAttrs={'resource-id': "com.instagram.android:id/full_name_change_limiting_textview"})

        simpleLog(adb, 'Page is loaded, getting old name to delete...')
        oldName = adbAuto.getElementSoup(
            adb.getScreenDump(), elementAttrs={
                'class': "android.widget.EditText",
                'resource-id': ""
            }
        )['text']
        adbAuto.clickOnElement(
            client=adb, elementAttrs={
                'class': "android.widget.EditText",
                'resource-id': ""
            }
        )

        simpleLog(adb, f'Old name is {oldName}, length is {len(oldName)}. Deleting...')
        adb.deleteText(length=int(len(oldName) * 1.2))

        simpleLog(adb, 'Inputting new name...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/prism_form_field_container'})
        adb.fastText(name)

        simpleLog(adb, 'Done, saving new name...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_action'})
        randomDelay(0.6, 0.7, 0.8)
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'})
        randomDelay(1, 1.1, 1.2, 1.3, 1.4)


    if username:
        waitForEditPage(adb, adbAuto)
        simpleLog(adb, 'Clicking to edit username...')
        adbAuto.clickOnElement(
            client=adb,  elementAttrs={
                'text': "Username",
            }, randomizK=0.1, yCorrector=75
        )

        simpleLog(adb, 'Waiting for edit username page...')
        waitForDumpElement(adb, adbAuto, elementAttrs={'resource-id': "com.instagram.android:id/username_lock_help_textview"})

        simpleLog(adb, 'Page is loaded, getting old username to delete...')
        oldUsername = adbAuto.getElementSoup(
            adb.getScreenDump(), elementAttrs={
                'class': "android.widget.EditText",
                'resource-id': "",
            }
        )['text']
        adbAuto.clickOnElement(
            client=adb, elementAttrs={
                'class': "android.widget.EditText",
                'resource-id': ""
            }
        )

        simpleLog(adb, f'Old username is {oldUsername}, length is {len(oldUsername)}. Deleting...')
        adb.deleteText(length=int(len(oldUsername) * 1.1))

        simpleLog(adb, 'Inputting new username...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/prism_form_field_container'})
        adb.fastText(username)

        simpleLog(adb, 'Done, saving new name...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_action'})
        randomDelay(0.6, 0.7, 0.8)
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'})
        randomDelay(1, 1.1, 1.2, 1.3, 1.4)


    if bio:
        waitForEditPage(adb, adbAuto)
        simpleLog(adb, 'Clicking to edit bio...')
        adbAuto.clickOnElement(
            client=adb,  elementAttrs={
                'text': "Bio",
            }, randomizK=0.05, yCorrector=73
        )

        simpleLog(adb, 'Waiting for edit bio page...')
        waitForDumpElement(adb, adbAuto, elementAttrs={'resource-id': "com.instagram.android:id/edit_bio_layout"})

        simpleLog(adb, 'Page is loaded, getting old bio to delete...')
        adbAuto.clickOnElement(
            client=adb, elementAttrs={
                'class': "android.widget.EditText",
                'resource-id': ""
            }
        )

        adb.deleteText(length=150)
        simpleLog(adb, 'Inputting new bio...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/prism_form_field_container'})
        adb.fastText(bio)

        simpleLog(adb, 'Done, saving new name...')
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_action'})
        randomDelay(0.6, 0.7, 0.8)
        adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/igds_alert_dialog_primary_button'})
        randomDelay(1, 1.1, 1.2, 1.3, 1.4)


    simpleLog(adb, 'Done. Returning...')
    waitForEditPage(adb, adbAuto)
    adbAuto.clickOnElement(client=adb, elementAttrs={'resource-id': 'com.instagram.android:id/action_bar_button_back'})
    return True