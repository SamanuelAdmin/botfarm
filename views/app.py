from fastapi import FastAPI

from .admin import admin, lifespanForAdminPanel

app = FastAPI(
    lifespan=lifespanForAdminPanel
)

app.mount("/admin", admin.app)