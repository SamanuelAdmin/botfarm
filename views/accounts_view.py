from fastapi import APIRouter

from db.data.account import *
from meta.exceptions import AccountNotFoundException, AccountNotFoundHttpException

from services.db_services.accounts_manager import AccountsManager


router = APIRouter(prefix="/accounts", tags=["accounts"])
accountsManager = AccountsManager()


@router.get("/all")
async def get_all() -> list[AccountSchemeCreate]:
    return list(accountsManager.getAllAccounts())


@router.get("/count")
async def get_count() -> int:
    return sum(
        1 for _ in accountsManager.getAllAccounts()
    )


@router.get("/get/{id}")
async def get_by_id(id: int) -> AccountSchemeCreate:
    try:
        return accountsManager.getAccountById(id)[0]
    except AccountNotFoundException:
        raise AccountNotFoundHttpException(id)
