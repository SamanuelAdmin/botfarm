import json
from typing import Any, Optional
import requests



class ApiConnector:
    _instance: Optional[Any]

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, adb_hub_api: str, timeout: float=2):
        self._adbHubApi = adb_hub_api if adb_hub_api[-1] != '/' else adb_hub_api[:-1]
        self._timeout = timeout

    def apiRequest(
            self, url: str,
            params: Optional[dict[Any, Any]]=None,
            headers: Optional[dict[Any, Any]]=None,
            data: Optional[str]=None,
            method='get', timeout: Optional[float]=None
    ) -> dict[str, Any]|int|Any:
        assert method.lower() in ['get', 'post', 'put', 'delete']

        try:
            with requests.Session() as session:
                r = session.request(
                    method.lower(), self._adbHubApi + url,
                    params=params, headers=headers, data=data,
                    timeout=timeout if timeout else self._timeout
                )
        except requests.exceptions.Timeout: return 408
        except requests.exceptions.ChunkedEncodingError: return 104
        except ConnectionResetError: return 104

        if r.status_code != 200: return r.status_code
        try: return r.json()
        except json.decoder.JSONDecodeError: return r
