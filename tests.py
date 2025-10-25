import datetime

from db.controller import DatabaseController
from meta.schemas import OrderModel
from repository.repository import Repository
from services.db_services import order_manager
from services.db_services.order_manager import OrderManager
from services.panel_manager.manager import PanelManager


apiKey = 'o2q92dp53loba3ftwyr5xqu6hd4w751fbfga3rm77p80ikdy8clukbwks7jilf5b'
db_controller = DatabaseController()

repa = Repository()
order_manager = OrderManager()
panel_manager = PanelManager(order_manager, apiKey)

def test_panel_manager():
    first = panel_manager.getFirstOrder()
    
    panel_manager.start()

test_panel_manager()
