import json
import os
from typing import Optional, Any

from meta.singleton import Singleton
from core.exceptions import IncorrectConfigsFormat, CoreIsNotInitialized
from core.core_configurator import CoreConfigurator
from core.logger import Logger, Log
from core.core import ICore, Core
from services.adb_manager import AdbManager


class Loader(metaclass=Singleton):
    '''
        Main class, which need to init and configure the Core
        Needs configuration file [configFileName] in the same
        dir with this file, or in configPath dir.
        Configs accept only in JSON format!
    '''

    def __init__(self, configFileName: str = 'core_configs.json', configPath: Optional[str] = None):
        self.configFileName = configFileName
        self.configFilePath = os.path.dirname(__file__) if not configPath else configPath
        self.configFullPath = os.path.join(self.configFilePath, self.configFileName)

        self._logger = Logger()
        self._configurator: CoreConfigurator = self._loadConfigsFromFile()

        self.__core = Core(logger=self._logger)
        self._logger.add(Log('info', 'Configuring core...'))
        self.__core.configure(self._configurator)

        self._logger.add(Log('info', 'Configuring done. Loading core...'))
        if not self.__core.load():
            self._logger.add(Log('critical', 'Core did not loaded.'))
            raise CoreIsNotInitialized()

        self._logger.add(Log('info', 'Core loaded. Ready to start.'))


    @property
    def logger(self) -> Logger: return self._logger

    @property
    def core(self) -> ICore: return self.__core


    def _loadConfigsFromFile(self) -> CoreConfigurator:
        self._logger.add(Log('info', 'Loading configuration from ', self.configFullPath))
        with open(self.configFullPath) as configFile:
            try:
                configs = json.load(configFile)
            except ValueError:
                self._logger.add(Log('critical', f'Failed to load configuration from ', self.configFullPath, '. Incorrect format!'))
                raise IncorrectConfigsFormat()

        for name in list(configs.keys()):
            if not name in CoreConfigurator.__dataclass_fields__.keys():
                self._logger.add(Log('warning', f'Unavailable config: {name}. Ignoring...'))
                del configs[name]

        return CoreConfigurator(**configs)


