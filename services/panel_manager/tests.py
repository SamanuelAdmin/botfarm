from db.controller import DatabaseController
from repository.repository import Repository
from services.db_services.order_manager import OrderManager
from services.panel_manager.manager import PanelManager


apiKey = 'o2q92dp53loba3ftwyr5xqu6hd4w751fbfga3rm77p80ikdy8clukbwks7jilf5b'
db_controller = DatabaseController()

repa = Repository()
orderManager = OrderManager()
panelManager = PanelManager(orderManager, apiKey)

def test_panel_manager():
    panelManager.startParse(do_not_use_in_production=True)

test_panel_manager()
