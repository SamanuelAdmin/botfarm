from dotenv import load_dotenv
load_dotenv()
import os

from core.loader import Loader



def main():
    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )
    core = loader.core


if __name__ == "__main__": main()
