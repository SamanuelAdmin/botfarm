from typing import Any, Optional
import requests



class ApiConnector:
    _instance: None|Any

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, adb_hub_api: str):
        self.adbHubApi = adb_hub_api if adb_hub_api[-1] != '/' else adb_hub_api[:-1]

    def apiRequest(
            self, url: str,
            params: Optional[dict[Any, Any]]=None,
            headers: Optional[dict[Any, Any]]=None,
            data: Optional[str]=None,
            method='get'
    ) -> dict[str, Any]|int:
        assert method.lower() in ['get', 'post', 'put', 'delete']

        r = requests.request(
            method.lower(), self.adbHubApi + url,
            params=params, headers=headers, data=data
        )

        if r.status_code != 200: return r.status_code
        return r.json()

