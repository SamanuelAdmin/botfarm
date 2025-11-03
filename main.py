import multiprocessing
import time
from typing import Optional
import uvicorn
from dotenv import load_dotenv

from core.dispatcher import Dispatcher
from services.db_services.order_manager import OrderManager
from services.panel_manager.manager import PanelManager

load_dotenv()
import os, sys

from scripts import debug_functions
# need to create_all! delete after adding migrations
from core.loader import Loader
from core.logger import Logger, setup_default_logger

from scripts import debug_functions
from scripts.login_script import loginScript
from scripts.selling_services_scripts import *
from scripts.edit_profile_info import editProfileInfoScript
from scripts.control_script import *


# some temp configs
DEBUG: bool = False


def getArgByFlag(args: list[str], flag: str) -> str|bool:
    """
        Getting data by flag, from any list. Use it for getting console command args.
    :param args: List with arguments.
    :param flag: Flag (usually started with "-")
    :return: False if arg not found, True is flag has no data after itself, str - if flag`s data found.
    """
    # if flag not found
    if flag not in args: return False

    dataIndex: int = args.index(flag) + 1
    # if flag is the last element at the list
    if dataIndex >= len(args): return True

    # getting data by index
    data: Optional[str] = args[dataIndex]
    # is the next element is a flag
    if data[0] == flag[0]: return True
    return data


def startDatabaseAdminPanel():
    # start admin panel. it is going to block process
    from views import app
    uvicorn.run(app, host="0.0.0.0", port=8000)



def main():
    global DEBUG

    clArgs = sys.argv[1:]
    mode = getArgByFlag(clArgs, "-mode")
    if mode == "debug": DEBUG = True

    from db.connector import DatabaseConnector
    DatabaseConnector().create_all()

    # init base logger and create local logger object instance (for this file only)
    setup_default_logger(debug=DEBUG)
    logger = Logger()


    # let system start correctly, without blocking
    databaseAdminPanelProcess = multiprocessing.Process(target=startDatabaseAdminPanel)
    databaseAdminPanelProcess.start()

    
    loader = Loader(
        configFileName='core_configs.json',
        configPath=os.path.dirname(__file__),
    )
    core = loader.core
    core.start()

    # panelManager = PanelManager(OrderManager(), os.getenv('PANEL_API_KEY'))
    # dispatcher = Dispatcher(core, panelManager)
    # dispatcher.load()
    # dispatcher.handler()

    for acc in [
        'cft.vladislav.04f2ah', 'cZ4FyXWMdpG5', '6MNXXM4AIIC722JAKBETWYAXFRNLXB6R',
        'mr.steven_831401', 'SXoHwOD79J44GR', 'GPPGI7T7Z4DHAD5RYL6SBIXF4YNORKWK',
        'msdonald58933', 'p5GET4aEskSZV6', '5K7H7LJTULNYTW6EKCW3BCG52IHV3I6G',
        'me0488der70to', 'tlWevWXrRA', 'SA2HJ6IBYDRJJOJLS2MXU453BUHCKAKD',
        'jhs.deborah.0e9v3t', 'On5aRcdQRu', 'P4NELDX6RAZPBTQ6FI6NO7RFCSF6F7ZF'
    ]:
        core.addServiceTask('988d5e424834365a33', loginScript, *acc)
    core.processService('988d5e424834365a33')

    for acc in [
        'utn.evans.xb6pfp', '6DXhrhjWBH28N4dC', 'QS2OUYQMWE5C3LVD6DHHFWLHADJ7W7TH',
        'william_davis700684', 'ZT4gc1MiJ52sBqM', 'O4LTODDLZN5HS7523PVJKVHMS7MT2HJ2',
        'rrb.miller.8pw98v', 'Rx57YCYt', '4APU32KVVOIEQUISZ2N4HLSLGYF3CXVH',
        'mestevenwilliamsaq51', 'Lc5YxVBFF4it5rLt', '2NUSF5SM6VTSS7PUWSIQWHJGHAM3LRHE',
        'ms.john73955', 'OuGTl2', 'NRQW4NDEWFF3WXF3UHU5KNCRNJLK6GUW',
        'ms.helen_al_d376', 'WwCu6Fb0I', '7ESPOVXASCMVPFVTDUZGXPJ7PXANBJG3',
        'ms.thomas_90313', 'I3vRwmerbxA8', 'UHQUOUYJA5K7DEGVJNE3SBIFDUKDPQMQ',
        'ms.jasondavis79037', 'Muxx47HsneS', 'OTPPIKY6JBRY5L2HETBY64CGEKR4H2VA',
        'spf.artur.h513fy', 'oMLxmR3o7fdQ', 'LBFEPG2JOKU5R2T5KBHLC5E7QUNZERAX',
        'macarol76727', 'lfzJeJN', 'NMW7XE2XU6VACSTQV3VPWDH35IT4JQYM',
    ]:
        core.addServiceTask('ce10171ac064981705', loginScript, *acc)
    core.processService('ce10171ac064981705')

    for acc in [
        '2306maryiwc.286', 'ZqWyfZGB', 'LNHYFLNZ5LTAO3SP62NPBJWXDDCKF3YH',
        'dr.thomasmoores6549351', 'nAFhbesllq', 'U6GTYWWFNNR5WYUOR6V66KQALCB4EXGH',
        'itd.garcia.k2428b', 'TCeKNn5R5', 'K3XUV75EVL5LFMJTEOFKDJD2YIKZL5BP',
        'dr.richard42800', 'nNK0lUJ11HWV', '4Y4ARAVH7WC3Z6267LHEYBXTRUX5CQOH',
        'mewilliamgarcias2383', 'JGC2tu94JaxcrOdX', 'YG5ENSKEMNYRHNOR2VNPR4CNRW3PUFKK',
        'drbrian_cartersx56780', 'qXvvTT', 'P2LX7PYYKUX7YKTKCF3CN7UJ6VZ5XWBW',
        'ycd.patricia.avn9cc', 'tqPClx', 'ZCOLTHBJOKXG6OP3GD5U55UV7U3VPGME',
        'mr.william585d21', 'Nv06qOKqGqfrz', 'WLUARJ47ECGN2ZIRGLQTG7OIWXWDQCNE',
        'fqb.kostja.22819d', 'QMpFSGluv', 'F7O4ZOK2VX4OPHNMDDA6LKX426UBXVOJ',
        'dcx.jackson.0ra1gs', 'uhvRZ4SUkDrlmj', 'XG4PVTP4L3AMO363UOR5HTUZWZAOR4UB',
    ]:
        core.addServiceTask('ce021712ab4f351805', loginScript, *acc)
    core.processService('ce021712ab4f351805')

    for acc in [
        'michael.andersonsj35546', 'qe8pnr04wH0Qw', 'IDEL3DENOYMDWKAK3AQVRNQ74SFNDNIR',
        'drstevenwrightsl68430', 'uQGm5kwsoplgg5ws', 'N2EYB7T2IEENSWOELLKUCQAT4EXVFONY',
        'jason441fj3', 'gilPa0fzkt', '4FYDKKTUVZMSUNV44KKQQKWEDBQGYY4P',
        'ehe.williams.wzk41w', 'Lk04MHsf', '7ROXE5LLEYI5MNBBIT4NAQ2LXSWP3AJX',
        'laura___me82', 'ncbYUecRkWe', 'HR64ZZGMTGYXTQD3T6VX4CEYFFNL2MJF',
        'rnk.donna.ea4tux', 'uDBKuvVeaPAJ3u', 'SQOYZRHGPZ3DRVIZRGE4ML4HX34BFAAT',
        'williamwhitef7s05', 'kgzp2ru4rsqOSKg', '2EOZISPRNZT67GCKPKKJ5N6SQCXEOCTP',
        'tdu.collins.xgposp', 'b9huT6KO8', 'RDCZJ422CPQU4U2OV4YQEX7EEFGJYMZ4',
        'messarah.clark31028', 'L394MX', 'BHED7BHQYXJFJ4XBFO4LEEH2VLGMSUBV',
        'ms_kimberly0315771', 'xwpVV4D', '4ZXVL4LS743JW4W5VPIULN5BZZWLFQRW',
    ]:
        core.addServiceTask('9887b636324a544e5a', loginScript, *acc)
    core.processService('9887b636324a544e5a')

    for acc in [
        'ms.carol.wright996078', 'TgIXkkaxf', 'NUTETSVFS5PAMTPREUUUAW4XYY2JB6LM',
        'drkevin.perezs593079', 'm1S7JLj6bCdpP19', 'PI4N4MSWE7AFEV5QNQCOKHCUEC23FITX',
    ]:
        core.addServiceTask('9887e933364e4c5534', loginScript, *acc)
    core.processService('9887e933364e4c5534')

    for acc in [
        'drkenneth.y67321', 'JgMvCY2WmR', 'CUA3XH2EZV3ZBH7SWO42O6HKZW2IVUAG',
        'dr_laura1411678', 'seQetHN06qEfHM1', 'ZVNKIT2A56TPVGOGYG4ONKTRQUGU3CR2',
        'michael_36031', 'gE7DECAU04', 'XEPBAKROH4Q4MESOBKPJCSHVS6W54D6H',
        'ms.mary4932806', 'sp8rHzb', 'JR4LFPOMAAG75BOOATB5DODC7MPYRPQO',
        'ms9994dvq32iv', 'WmJ77G', 'IJYADBHAIGMJXRBY2RJLXBRYCNXISUWH',
        'ms.susan_8036', 'oNEFTJrfQIkI', 'Z6DT3BARLIKP5TDNSHIJSYVJ3DTX7YKE',
        'william_johnsonsx79846', '3UUlrzLa', 'TU6UBLANEIPESXWA6X6FDZMTJACTK62Z',
        'richard.walker2031185', '7C9R6ZWM194G7FML', 'O5FUKUXTBA4SBGGSPMTHJNGMMPSC6T7P',
        'david_59543', 'YIxjqjSCX', 'N3WMMVDCTXDJWCCKVK52UVFVLYBDMUH3',
        'dr.joseph.youngs9482987', 'sNMGzPB8RvI90y', 'G3KFSMIODAB5P2AEL62XKOZEEJFC2L3M',
    ]:
        core.addServiceTask('9887bc465035504945', loginScript, *acc)
    core.processService('9887bc465035504945')

    # time.sleep(60)
    # core.stop()


if __name__ == "__main__": main()
