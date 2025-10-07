from typing import Generator

from repository import Repository

from db.data.account import Account
from db.data.connected_email import ConnectedEmail
from db.data.device_id import DeviceID
from meta.exceptions import AccountNotFoundException, IncorrectDataFormatException



class AccountsManager:
    """
        The only one possible way to work with database accounts.
        Must-have layer between core/main program and repository.
    """

    def __init__(self):
        self.repository = Repository()

    def loadFromDump(self, dump: str) -> tuple[Account, DeviceID, list[ConnectedEmail]]:
        parts = dump.split('|')
        if len(parts) != 5: raise IncorrectDataFormatException()

        try:
            creds, user_agent, device_ids, cookies, connected_emails = filter(
                lambda x: x, dump.split('|')
            )

            login, password, key = creds.split(':')
            device_id = DeviceID(
                *device_ids.split(';')
            )

            cookies = {
                line.split('=')[0]: '='.join(line.split('=')[1:]) for line in cookies.split(';')
            }
        except: raise IncorrectDataFormatException()

        connected_emails = [
            ConnectedEmail( *line.split(':') ) for line in connected_emails.split(';')
        ]

        account = Account(
                login = login, password = password, key = key,
                user_agent = user_agent,
                cookies = cookies,
                device_id = device_id,
                connected_emails = connected_emails
            )

        self.repository.create(account, device_id, connected_emails)
        return account, device_id, connected_emails


    def getAccountById(self, _id: int) -> tuple[Account, DeviceID, list[ConnectedEmail]]:
        account = self.repository.read(Account, _id)
        if account is None:
            raise AccountNotFoundException(_id)

        return account, account.device_id, account.connected_emails


    def getAllAccounts(self) -> Generator[Account, None, None]:
        for account in self.repository.readAll(Account): yield account


    def deleteAccountById(self, _id: int):
        self.repository.delete(Account, _id)


    def updateAccountById(self, _id: int, **kwargs) -> None:
        self.repository.update(Account, _id, **kwargs)
