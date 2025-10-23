import requests
import json

from services.panel_manager.exceptions import PanelApiServiceError, UnknownMethodError
from services.panel_manager.enums import PanelApiMethods


class PanelApiService:
    def __init__(self, apiKey: str) -> None:
        self._apiKey = apiKey
        self._apiBaseUrl = 'https://thepanel.top/admin/adminapi/v2/paths/orders/'

    def _getJson(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise PanelApiServiceError(f"Не удалось получить json из ответа. {e}")

    def _requestApi(self, method: PanelApiMethods, endpoint: str) -> requests.Response:
        try:
            if method == PanelApiMethods.GET:
                res = requests.get(self._apiBaseUrl + endpoint)
            elif method == PanelApiMethods.POST:
                res = requests.post(self._apiBaseUrl + endpoint)
            else: res = None
        except Exception as e:
            raise PanelApiServiceError(f'Unknown error: {e}')

        if res is None:
            raise UnknownMethodError(f'Method {method} is unknown!')

        if res.status_code != 200:
            raise PanelApiServiceError(f'The status code is {res.status_code}')

        return res

    def getOrdersJson(self) -> dict:
        res = self._requestApi(PanelApiMethods.GET, '')
        return self._getJson(res)
    



