from services.adb_manager import AdbManager

from scripts.edit_profile_info import *
from scripts.selling_srevices_scripts import *

# loading .env variables
from dotenv import load_dotenv
load_dotenv()



def main():
    TEST_SERIAL = '98896a374256375548'

    adbManager = AdbManager('http://10.0.0.3:15991')
    adbAuto = AdbAutoManager(adbManager)
    adb = adbManager.loadSerial(TEST_SERIAL)

    # login script
    # loginScriptV2(adb, adbAuto, 'ms.jason.bakers25731', 'RLpk6jDCSrEt', '4Q3FI3OTH7VYVRJGFJFZZ4NJ6GZSDRFQ')
    # print(adb.getScreenDump())
    # editProfileInfoScriptIG(
    #     adb, adbAuto,
    #     username="leonardo_d_art98",
    #     name="Leonardo Della",
    #     bio="Pittore classico moderno",
    # )

    editProfileImage(adb, adbAuto, 'C:\\Users\\PC\\Desktop\\female\\janellecaruso_\\single_photo_12.jpg')

    # likePost(adb, adbAuto, 'https://www.instagram.com/p/DAbsb11qEYw/')
    # followAccount(adb, adbAuto, 'https://www.instagram.com/psptm5/')

    # adb.makeScreenshot()
    # adb.downloadFile()
    # adb.deleteText(length=10)


if __name__ == "__main__": main()
