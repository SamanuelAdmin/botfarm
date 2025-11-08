import json
import os
from typing import Optional

from core.hardware import AdbClient
from core.middleware.adb_checker import AdbChecker
from meta.singleton import Singleton
from core.meta.exceptions import IncorrectConfigsFormat, CoreIsNotInitialized
from core.meta.core_configurator import CoreConfigurator
from core.logger import Logger
from core.core import Core


logger = Logger()

class Loader(metaclass=Singleton):
    '''
        Main class, which need to init and configure the Core
        Needs configuration file [configFileName] in the same
        dir with this file, or in configPath dir.
        Configs accept only in JSON format!
    '''

    _configurator: CoreConfigurator
    __core: Core

    def __init__(self, configFileName: str = 'core_configs.json', configPath: Optional[str] = None):
        self.configFileName = configFileName
        self.configFilePath = os.path.dirname(__file__) if not configPath else configPath
        self.configFullPath = os.path.join(self.configFilePath, self.configFileName)

        self._configurator: CoreConfigurator = self._loadConfigsFromFile()
        self.__core = Core()

    def load(self):

        logger.info('Configuring core...')
        self.__core.configure(self._configurator)

        logger.info('Configuring done. Loading core...')
        if not self.__core.load():
            logger.critical('Core did not loaded.')
            raise CoreIsNotInitialized()

        logger.info('Core loaded. Ready to start.')


    def setAdbChecker(self, adbChecker: type(AdbChecker)) -> None:
        self.__core.adbChecker = adbChecker


    @property
    def core(self) -> Core: return self.__core

    def _loadConfigsFromFile(self) -> CoreConfigurator:
        logger.info('Loading configuration from ', self.configFullPath)
        with open(self.configFullPath) as configFile:
            try:
                configs = json.load(configFile)
            except ValueError:
                logger.critical(f'Failed to load configuration from ', self.configFullPath, '. Incorrect format!')
                raise IncorrectConfigsFormat()

        for name in list(configs.keys()):
            if not name in CoreConfigurator.__dataclass_fields__.keys():
                logger.warning(f'Unavailable config: {name}. Ignoring...')
                del configs[name]

        return CoreConfigurator(**configs)


    def _add_checker(self):
        pass