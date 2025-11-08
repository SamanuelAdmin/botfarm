from core.hardware import AdbClient
from core.logger import Logger


logger = Logger()
CHECKING_COMMAND = 'ping -c 1 -W 1 google.com'

def connectionCheckFunction(_, adb: AdbClient, *args) -> bool:
    """
        Function for adb checker (waining checker).
        Returns True if client is connected to the internet.
        FIRST ARGUMENT - CHECKER OBJECT INSTANCE!
        DO NOT USE FIRST ARGUMENT!
    """
    result: bool = False

    try:
        commandResult = adb.sendAdbCommand(CHECKING_COMMAND)

        """
        Successful result seems like:
        
        PING google.com (142.251.140.78) 56(84) bytes of data.
        64 bytes from sof04s06-in-f14.1e100.net (142.251.140.78): icmp_seq=1 ttl=116 time=158 ms
        
        --- google.com ping statistics ---
        1 packets transmitted, 1 received, 0% packet loss, time 0ms
        rtt min/avg/max/mdev = 158.808/158.808/158.808/0.000 ms
        
        So, "1 packets transmitted, 1 received, 0% packet loss" - means that device has access to the internet.
        Anything else - means no.
        """
        assert commandResult.get('status')
        assert commandResult.get('result')

        commandResult = commandResult.get('result')
        if "1 packets transmitted, 1 received, 0% packet loss" in commandResult: result = True

    except AssertionError: pass # for easy skipping the end of the func
    except Exception as e:
        logger.debug(f'{adb.serial} Got unexpected exception in internetChecker func: {e}')
    finally:
        return result