from fastapi import FastAPI

from .admin import admin, lifespanForAdminPanel
from .accounts_view import router as AccountsViewRouter

app = FastAPI(
    lifespan=lifespanForAdminPanel
)

app.include_router(AccountsViewRouter)

app.mount("/admin", admin.app)