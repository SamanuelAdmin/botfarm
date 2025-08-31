from instagrapi import Client
from instagrapi.types import Media

from db.data.account import Account
from db.data.connected_email import ConnectedEmail
from db.data.device_id import DeviceID

from .fa2 import get2FACode


class ApiAccountManager(Client):
    def __init__(
            self, account: Account, deviceId: DeviceID, connectedEmails: list[ConnectedEmail],
            proxy: str = None
    ):
        self.account = account
        self.deviceId = deviceId
        self.connectedEmails = connectedEmails

        super().__init__()
        self.delay_range = [0.5, 1]

        self.set_user_agent(account.user_agent)
        self.set_uuids({
            'android_device_id': deviceId.device_id,
            'uuid': deviceId.uuid,
            'client_session_id': deviceId.session_id,
            'phone_id': deviceId.phone_id,
        })

        if proxy is not None:
            ipWithoutProxy = self.getClientIp()
            self.set_proxy(proxy)
            ipWithProxy = self.getClientIp()

            if ipWithProxy == ipWithoutProxy:
                print(f'Login without proxy. IP: {ipWithProxy}')
            else: print(f'Login with proxy. New IP: {ipWithProxy}')

        self.login(
            account.login, account.password,
            verification_code=get2FACode(account.key)
        )

    def getClientIp(self, url: str="https://api.ipify.org/") -> str:
        return self._send_public_request(url)

    def change(self, **kwargs) -> None:
        self.account_edit(**kwargs)

    def like_by_url(self, url: str, **kwargs) -> None:
        self.media_like(
            self.media_id(
                self.media_pk_from_url(url)
            ),
            **kwargs
        )

    def comment_by_url(self, url: str, comment: str) -> None:
        self.media_comment(
            self.media_id(
                self.media_pk_from_url(url)
            ), comment
        )

    def follow_by_username(self, username: str) -> None:
        self.user_follow(
            self.user_id_from_username(username),
        )


    def get_media_info_by_url(self, url: str) -> dict:
        return self.media_info(
            self.media_pk_from_url(url)
        ).dict()