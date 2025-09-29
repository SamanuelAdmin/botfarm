from typing import Generator
from db.data.account import Account
from db.data.connected_email import ConnectedEmail
from db.data.device_id import DeviceID
from meta.exceptions import AccountNotFoundException
from repository.accounts import Repository


class AccountsManager:
    def __init__(self):
        self.accountRepository = Repository()

    def loadFromDump(self, dump: str):
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

        self.accountRepository.create(account, device_id, connected_emails)
        return account, device_id, connected_emails

    def getAccountById(self, id: int) -> tuple[Account, DeviceID, list[ConnectedEmail]]:
        account = self.accountRepository.read(Account, id)
        if account is None:
            raise AccountNotFoundException(id)

        return account, account.device_id, account.connected_emails


    def getAllAccounts(self) -> Generator[Account]:
        for account in self.accountRepository.readAllAccounts(): yield account

    def deleteAccountById(self, id: int):
        self.accountRepository.delete(id)

    def updateAccountById(self, id: int, **kwargs) -> None:
        self.accountRepository.update(Account, id, **kwargs)
