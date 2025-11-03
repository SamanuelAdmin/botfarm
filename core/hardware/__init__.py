from .manager import Manager, AdbClient
from .adb_auto import AdbAutomatization, PostActions, postAction, POST_ACTION_CONTRACT
from .dot import Dot

AdbManager = Manager
AdbClient = AdbClient
Dot = Dot
AdbAutomatization = AdbAutomatization
PostActions, postAction, POST_ACTION_CONTRACT = PostActions, postAction, POST_ACTION_CONTRACT