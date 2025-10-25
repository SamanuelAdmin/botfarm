import requests
import json

from meta.exceptions import PanelApiServiceError, UnknownMethodError
from services.panel_manager.enums import PanelApiMethods

from typing import Any


class PanelApiService:
    def __init__(self, apiKey: str) -> None:
        self._headers = {
            'X-Api-Key': apiKey
        }
        self._apiBaseUrl = 'https://thepanel.top/adminapi/v2/orders/'

    def _getJson(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            raise PanelApiServiceError(f"Could not get the response. {e}")

    def _requestApi(
            self, method: PanelApiMethods, endpoint: str, queryParams: dict[str, Any]|None=None
    ) -> requests.Response:
        try:
            if method == PanelApiMethods.GET:
                res = requests.get(
                    self._apiBaseUrl + endpoint, params=queryParams, headers=self._headers
                )
            elif method == PanelApiMethods.POST:
                res = requests.post(
                    self._apiBaseUrl + endpoint, params=queryParams, headers=self._headers
                )
            else: res = None
        except Exception as e:
            raise PanelApiServiceError(f'Unknown error: {e}')

        if res is None:
            raise UnknownMethodError(f'Method {method} is unknown!')

        if res.status_code != 200:
            raise PanelApiServiceError(f'The status code is {res.status_code}. {res.text}')

        return res

    def getOrdersJson(self) -> dict:
        res = self._requestApi(PanelApiMethods.GET, '')
        return self._getJson(res)

    def getOrdersJsonCreatedFrom(self, createdFrom: float) -> dict:
        """
            Order creation UNIX timestamp (lower bound).
            Sorting: "sort": "date-asc"
        """
        res = self._requestApi(
            PanelApiMethods.GET, '', {'created_from': createdFrom, 'sort': 'date-asc'}
        )
        return self._getJson(res)

    def getSortedOrders(self) -> dict:
        """
            Gets sorted list by date-desc
        """
        res = self._requestApi(
            PanelApiMethods.GET, '', {'sort': 'date-desc'}
        )
        return self._getJson(res)
    



