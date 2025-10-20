import multiprocessing
import time
from typing import Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()
import os, sys

from scripts import debug_functions
# need to create_all! delete after adding migrations
from core.loader import Loader
from core.logger import Logger, setup_default_logger

from scripts import debug_functions
from scripts.login_script import loginScript
from scripts.selling_services_scripts import *


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

    accountsList = [
        # ('ms.edwardlewiss39667', 'P9XM8e1', '2MX5HFZ4B65IHQZBTUYLOCQER5JVK45T'),
        # ('skp.umsorokin.k98lkg', 'XtukpF25dN8N0VPo', 'DUURBTHKWP55AC35ZLIB3Y443GUOQ6CQ'),
        # ('dr.george_moores262x', 'BBfgchyWGgK9r', 'RHB5I76OK5Y4PLZO55CIMLUX6VMRZ7PG'),
        # ('merobert_wright91278', 'hnxnX1kI', '2U6WW7JFY44BXFKVS2YWMI52D7RVMFLF'),
        # ('mschristopher_93514', 'n0xM8h7w0f', 'GZNNABCX35GLD56VAWOA272RXNZCFXSM'),
        # ('ms.donald_moores27666', 'r1zrE1jyLM', 'X4WEDIBLF2PCJ4J35E5VOOSUEQRBFHWS'),
        # ('ms.thomas.0830', 'sfj1NF0zi2QJs6a', 'BMAZBNCQHGW65A6YVAVMPDOFZCSSYRLF'),
        # ('dr.robert_turners133445', 'YcE6KxV', '7VVQENPIH3GFKWLNXMEUHMNTQA2ZK3MZ'),
        # ('donald42535', 'fRBfN2ciOTKt', 'XFQHW3XUONJWSLVA6FEI2YCZU5E6OFNX'),
        # ('dr.george.perezsi0235', 'I072rgzMxG', 'DBAOPFBRPGUPRL6MXCSYK6WZEVOPEXPL'),
        # ('4767.sandracqj500', 'SS2dP8p', 'ZGEDWTTDMUSEK3DM4HM4DMJMWEMEBIOO'),
        # ('jason_hernandez0948808', 's3BJQo4SN', 'HD5EQKHRWWBHIQJHDSPR6MXKEV4SILYJ'),
        ('drdaniel_robinsons0869i', '4hTJieKTv2', 'DOSLQ5ZTFU7DVEFTSBMPQ7JJEGB7ZCX2'),
        # ('yfj.cvdanilov.fhi97p', 'KNnLDOA', 'HWKLURQUVRBGAYOEXWBSWKRAXKIQXDGK'),
        # ('mejohn.scott754611', 'zfYI2q8R1jfWmLZo', '7H6YZTFV4CZVB67QIETBMSL42CLTVXZ5'),
        # ('nfk.vova.604qkn', 'JuE40b7o', '3AT3AW4XVCYEGXQKCIUCFCPBKIBBAMVD'),
        # ('dr.brian_91022', 'bfX4PNg8EQ7yB4w4', 'NJFXRIOBVFASHGAM5Z2EVFZDZDI2TCDU'),
        # ('mrsedward_millers2486', 'M6dq3IEQGvrwSWiV', 'OXQLFO6H2FN6NJPE64VVMKJ6EYNQZPNV'),
        # ('kevinmitchell07527', '004V2KzaVw4', '4TQNAK4PPWV7NCNJLTK7VR6LFQQ2TRYC'),
        # ('dr.stevencampbells620878', 'sLSeu3', 'TACFNQLV7Y6VCDMUVQ56MWWGURVKTGT3'),
        # ('dr.john.johnsons627f', 'S5A6ZQhaXT9oC', 'LSJTLEGSFZ4DKEDC7YBVJ25JO3UP2YLF'),
        # ('ola.donald.8yrs8e', '8G3TXSoqqedDsP6', 'R3WU644SFQMFIQRD3Z5RU3MDLMTDEO2A'),
        # ('dr.donaldperezs96959', 'j5qOrY3gj', 'G4OKHP4C4C4IZ5XA22R2SBWCS4QMDKXU'),
        # ('drsteven_evanss2905320', 'dSmRMyT19YbqrY0L', 'Q54MEFWCKTBI5R2V5IBNFPBRAMG47S6I'),
        # ('urv.phillips.i99e6m', 'Hb49L64', '7F6M664ES2U5HBUCDC6ARSPDCLOY6NOW'),
        # ('mrsanthony_wilson3816', 'a1nuG0H7rl', '57TQ3PWVBLGTGURSNEY7MDVAYUDKZEYV'),
        # ('michael.martins88110', 'PL8AZi', '4MY6GI4PUCHBJKMG2EIABBHMEMKZ4POY'),
        ('mrsdaniel.hill5369218', 'pjbdDiJoXs1KwBDG', 'DZMR4YXZPUJL3YZO6NZE7Z6BUP3DAWGL'),
        # ('mepaul_hill44357', 'fcT8M90LjE7', 'EJFNFYQATMESQIINPLZIF5MS2LF5E2IN'),
        # ('drrobert_garcia85816', '0zB1RqOZmK1iPaAR', '2AYZFXKQRPUHJR5Z2CEN4JGFQDL7TTHQ'),
        ('uzq.linda.1r7fka', 'tvuUoFz7tHnK1', 'ILFOS4MORDMUTQDUPQMCJXQN6ZIU5RXM'),
        ('drrobert.perez17800', 'uqi3rNbAu', 'HVCTQORQXXM6O6FJ6UHUUHWNGH42AXSE'),
        # ('mrsgeorge_parkers7846555', '5KJqmVf7', 'XT2JRRHPUV2OW5OW6M3BRJL34HIL6YBL'),
        # ('jwo.carol.uhmbau', 'bpQYzrH9x3A', 'DZ3A226A2JXX5Z7TIHE4PVOVAGZJEL4X'),
        # ('ms.edwardrobertss226531', '339vy1bt', 'N2UANHITQDGYHX3BV2UYCFL2UUKZKLOD'),
        # ('ms.josephadamsq88990', 'G7CUnKEa', 'UJLW44P24JZU2GOQAB5PV7JCOTWBQSMF'),
        # ('drchristopher.49044', 'YmcwDgyh9', 'CD53UK6W72V6DRTCKF7AB44APAX4P7N5'),
        # ('icn.thomas.90605b', 'rHYcR0n', 'RUX46SPINCNCUMRSVBFWLUOBGMEQRHGQ'),
        # ('memark_wright242497', 'dDV3doA', 'G7SGVZCOLBR3GE42DNGD335ZCLCDOCBM'),
        # ('1406.margaretrsh400', 'vEUgOtGTCaMxc', '2MDEVBCNVF3PG236N7422HOUXEPFOOMJ'),
        # ('georgerobertss5690', 'uKyUpk', '6T554VWLCOPTTL5FPIDUISK2ZDZM3JAG'),
        # ('ms.mark.5558212', 'wXGrnpeFbC', 'RDBHDXLEPKBQRVABBEJWMQRVIM5INYLL'),
        # ('mrsmichael.lees3124490', 'RjBeDfC533bKI', 'ZUGGNHXCRASRDEEBTEQ3QZMH24GQNFLP'),
        # ('joseph.0937422', '1UBvkZ8T718Gke4x', 'ZNJTZE7B42EMLZ67JVZ3LPNUA4AZDABE'),
        # ('ms.michael_4656627', 'VgcMrAo4pLDx', 'T742POBVZSOQPO25B6MVTOHW7CHKRM4F'),
        ('msronald_2737', 'XxUwBi7RKKd6', '53JVGFAYVQPTNZA42CVLCBKTCIVJE3PZ'),
        # ('iol.brian.c88wkm', 'ENx5anC', 'O23SD7OSULIBYAD3MWX2FWRCVLFBVHEX'),
        # ('drjoseph.nelson45747', 'ifmOq5bYpfQxYgoH', 'RHA7JTHSAFHFKOH7YMFOQIQGSMI2WPYF'),
        # ('mspauls76857', 'gfZT2opmF68vt7', 'FPMDRQD27J6SG6YEI5QS25MFPCEEH3N3'),
        # ('drmark_270y', 'hfsI9E', 'VJPEHGVP7ZQZBGXEU7JT5OSWV2VETNTE'),
        ('ms.kevin.anderson2646577', 'pGSOw1CbnXv43ujH', '6BRPLHT3BSSYBGXH5WMROZO7JXY5IYR2'),
        ('qrr.igor.e18p7g', 'Dbu2p6eW', 'AB5VNBBFK4Q4L7FVVIORQCTZWTOGRAZO'),
        # ('dranthony.harriss0604189', 'Dts3oK', '7VKHPR7OCUCF7SFKTD7GRVIP6GNQ7XBZ'),
        # ('qsn.william.3m8ikg', 'rjPodOP0OwTuY3p', 'FS7CNOBTYVHLZQTEFBLGLMOIWGLBD2R6'),
        # ('msanthony.860600', 'quBuIF6', 'Z3O33UU25UXUW4LTIEZWY3RKH63VC7UK'),
        # ('memark.williamss5234891', 'aYxPgP', 'CXV2U2PX7NBYD3CBFKP3AC3CG7D5YNNP'),
        ('drpaulmartinez316778', 'hn4PRfv7DYyG', 'ZWM5DY7O5HMN66RYIRFEQYF7G2AYYHBM'),
        ('meanthony_hernandezs29725', 'BKem7rlKzGuY', 'RWFLGDORGGEIRIZZERZTU6QOGWBHWDNN'),
        # ('gea.wright.7d8i2x', '1OINu9HGns', 'KNBP42ZXMICBMDJOFYZCMTYECECEU6RE'),
        ('mewilliam.13868', 'mV1ulfKz7guG', '6HG7KBFL4RMGNCJYA7KKPXEF5VG7FH7I'),
        ('msthomas.allena79888', '7Sotbolm3uGFNU', 'BFIL72WXXFWIQIHL3VYR23C2HYQPAX6C'),
        # ('mecharlesandersons807975', '22orbF5f5gXTo6r', 'KIQ6URSJXJPTXBV24MEQCNKVF7XN4HP2'),
        # ('mrsjeffcampbells122414', 'sl8DuQ8xJekKc8H', 'FQVCF77UZLFHMZ5DVBI3ZMQVOYTCVCXX'),


        # ('mrscharles_7307', 'tDHFC6xy0NvWiz', 'VY6SJB7OLTKFM4JENK5AWV7KYHFWG6ZK'),
        # ('xsu.whkarpov.fw7q4d', 'HaFRYsPXtj9x', 'ARU6VW4ODFZMOIWSY7UZOK5VYQQWUJSH'),
        # ('msrobert.486783', '8CRGBzkT', 'YLW5AMIVT6X3XM2CTAZBCPCOR4FP3PKK')
        # ('mskevincollinss28077', 'tJAn3WnBSV', 'BN7E7SQWSYGGO6ISUDEQPBVH7EJ4G2EB'),
        # ('qdz.king.8t94ph', 'NeZKdGGZtQKzZEn', 'S3QJ5CEC2MKXYGCDZ5SASNJMO6XEPTOI'),
        # ('drkevin_clarks15048', 'fVmsjUg6', 'L6YIRKW5JS7UTZCI6WDPIRDSHTQVBWRW'),
        # ('xoo.kostja.76hepj', 'TonmY7xoDGENhlu', 'Y5GQY6SSEOFIU2OONGRBLGAJFCH25UMC'),
        # ('daniel_daviss055938', '6oNnY4q4iQpN', 'FYDKF262ZUWK72YPM5Z37TBPQTT5IXGU'),
        # ('msanthonycollinss0803417', 'EMfi7pQ', '4VW3FVA3JYOEQZMS6MKOTQQEDXRPM4PJ')
        # ('methomasbrowns58244', 'bx2i7O7', 'X3RAIUWPH3THOW4CTPB2VTXAT3IXNSDW'),
        # ('dr.jamesclarks9230719', 'zrFnm3b4d2WMbL', 'X4OOAX2QAM2FMQCHEHW5XSOPWQ337NKE'),
        # ('afp.edwards.sf3r3y', '9Qp5pmxW1I', 'DDDWFDLU5G37C5RJLBPTMZDP56KPIFRC'),
        # ('msjoseph_collinsw2251', '4dNl5vO', 'GAVCENWYXWXI7VJZNIJYS2X3WMPZWUJ4'),
        # ('6182.dorothybcj040', 'xNHlJfrRtcW', 'GBPPOYZVQDSJYK5WSJZFFECC6GBUJBBM'),
        # ('mrsthomasgreens21573', 'fcym4sH81jicif', '2UFS6YGROTJ6K2PV47ZOTSOVS7CSCDGY'),
        # ('mrsjohni87643', 'NllExfsbpjD', 'ZBUEJOD7ZUT73VYR47DS6NBIBTPCBXNF'),
        # ('por.william.u0e72u', '8UPHBF', 'GWOGPKA6S2UPE36HCQ3JHIHW4IWMJND2'),
        # ('gtb.jura.k6523e', '0BSloSCkg62', 'BWEUM6WS5WRYXIQ7WSIONF4VQM4TPKU6'),
        # ('william_jackson78183', '5a6uCQ6KQn', 'G4CFJ5NEWL37FNUPJB2PJTRPUSOYLW34'),
        # ('3695.ruthkje878', 'jbBBUbWA8', 'KVFJNARO5CZHIWXMD36XQMKUQCE4ANN7'),
        # ('ebl.susan.8duvgb', 'vCHjpY', 'F64VAEA5RQ5R3LSGOWCMXZCECCPWXJTL'),
        # ('mscharles.v86868', 'fj0fNHt0w3', 'ATQR4GYKYZSPKMSCMJOKCZMUSN42SAWA'),
    ]

    # DIDNT USED ACCOUNTS
    # ('zki.adams.6n6i9p', 'eAJ65TJKsVv', 'H5WTOYIGDWOA53RLMBCJ2VSO273Q65CK'),
    # ('iej.smith.m693pd', 'gSU2szNX1eWY', 'NZBWSUWAX4KZY5FZ7ECHCH4CP5SJPOFF'),
    # ('thomas.07626', 'th2MrDuoKBcyToA', 'RVK6A2TRXNXZHSYEBFDIEIJ6DJRQD552'),

    # PROBLEMS ACCOUNTS
    # ('drmichael_x0865', 'mftPM0v', 'HTEQNZBS7VHYSQVOEDO23CDMY7ITBEJG'),
    # ('mschristopherwrights11832', 'HbYm3pBMVtK', 'BQTLCQI4IYMXEQEU5C2LMQWKIB4HRJVP'),
    # ('ms.michael.adamss82274', 'mhMzmuND', 'RB2ZUOQAZXNP57JD5BYX7JPQPPD23SXQ'),
    # ('mrspauljohnsons45090', 'X16d0dd7Zf2O', 'C3WRXH6AV2LKKJ7QMVC6ZEVAQGAHW6VJ'),
    # ('dr.david251030', 'Ahie0KFuWH', 'KZMRRM3E6T76OTJJPEIYH2WIBBIZZM47'),
    # ('msjohn_carters263986', 'BFGtyB4tx', 'HESQ35A2VLCHTTICFA7OOSZUSJBC3T3Q')
    # ('msjeffcollins89057', 'Qy4bvk6bdk8PWuE', 'HR6DOJ3RUUNLNAL6NSBTUMLXAKUW45HU'),
    # ('ms.edwardbrown79192', 'xHtYmUtSIzDq', 'HMP5WYBK7SXO6MFKSOCMZQV4HOZJFUPZ'),
    # ('ms.steven.walkers55170', 'U8fsFCmuCqku', 'QYAL6KUDC2RA2GFDA3ARVG4VABJ5N6ZC'),
    # ('brian_202475', 'BvzXUx1dnuLT', '6GJGTRWJWYWNZTY7Z544UBZIOF3DIG67'),
    # ('dr.jeff_wright45454', 'nPW7KpAD', 'ZZIFK6UE4CF6IYK3RCDZDHSN4COD5HC7'),
    # ('drjoseph.mooreh73938', 'yT5PqwF', 'SPMSEXLDUYXS3ASKMLALF6OIVONJ6ZBN'),
    # ('steven672a', 'dnR3cKjPUQ36QR', 'WCNGW7KZLILWXR3IUWAX7XBF7SQKHTA4'),
    # ('jason.thomaso24521', '8CXs6fvG0ffO', 'ZMUBWJJHYNRG4FY4E3OUZ6G5VI2ZG32A'),
    # ('lva.igfilatov.12971f', 'rJrxw7Z', 'VFEGULZFGU2QY67T3DAL4Z5DJZ6E7NZ6'),
    # ('charles_thomassh64008', '7kHvVpdujyi1', 'MZVTTLRKQ74XHZ2WZJQ6NJUZ4CFJDTTF'),
    # ('jason.perezs82937', '2or2dN', 'S4HMIFUSIITEBIGAGOC6GT4LXSFWFSNR'),
    # ('lma.sarah.158z7b', 'VtBAJF8WlH', 'UOHTRQ7DO34O4FSHY443XHVJ5FGJBQ4N'),
    # ('dr.michael.26466', 'hPhVJjwEdNa', '42MWEP6AA6MRAKETUMMTSHZ4G6B5BAXC'),
    # ('mrsmichael_phillipss51927', 'XjWtwVZoCGgVMr', 'PBIUBHHZZULNVBHJUI5T3UELW6MAOWUW'),
    # ('msedward_johnsons32598', 'J018ZVX2OI', 'VJ75XZ4IWXMUIRLGX4XXCAATWSQAKCM5'),
    # ('ms.michael_451229', 'xhY8ntuh4', 'RJHWUISIDNVC55TY2JFQLUGX774YMV2V'),


    doNotUseList = [
        '98893a363136463157@3c067526',
        '98883743344a4e5a30@3c067526',
        '988d91475a37354930@3c067526',
        '98897a305531504a4c@3c067526',
        '988adc484735314950@3c067526'
    ]

    # servicesList = [ serviceId for serviceId in core.servicesTable if serviceId not in doNotUseList ]
    #
    # accountIndex = 0
    # serviceIndex = 0
    # while accountIndex < len(accountsList):
    #     core.addTaskToService(
    #         servicesList[serviceIndex], loginScript, *accountsList[accountIndex]
    #     )
    #     logger.info(serviceIndex, accountIndex, servicesList[serviceIndex])
    #     accountIndex += 1
    #     serviceIndex = serviceIndex + 1 if serviceIndex + 1 < len(servicesList) else 0
    #
    #
    # for serviceId in servicesList:
    #     core.processService(serviceId)

    # core.addTaskToService(
    #     '988e9034574a4d5831@3c067526', likePost, 'https://www.instagram.com/p/DN5LWYJjNhq/',
    # )
    core.addTaskToService(
        '988e9034574a4d5831@3c067526', commentPost, 'https://www.instagram.com/p/DN5LWYJjNhq/', 'Guess what? Coconut!',
    )
    core.processService('988e9034574a4d5831@3c067526')

    # time.sleep(60)
    # core.stop()


if __name__ == "__main__": main()
