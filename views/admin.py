from contextlib import asynccontextmanager

from crudadmin import CRUDAdmin
from fastapi import FastAPI

from db.data.account import *
from db.data.device_id import *
from db.data.connected_email import *
from db.connector import DatabaseConnector


databaseConnector = DatabaseConnector()
ALLOWED_ACTIONS = {"view", "create", "update", "delete"}


# Create admin interface
admin = CRUDAdmin(
    session=databaseConnector.getAsyncSession,
    SECRET_KEY="your-secret-key-here",
    initial_admin={
        "username": "admin",
        "password": "password"
    }
)

# Add models to admin
admin.add_view(
    model=Account,
    create_schema=AccountSchemeCreate,
    update_schema=AccountSchemeUpdate,
    allowed_actions=ALLOWED_ACTIONS
)

admin.add_view(
    model=DeviceID,
    create_schema=DeviceIDSchemeCreate,
    update_schema=DeviceIDSchemeUpdate,
    allowed_actions=ALLOWED_ACTIONS
)

admin.add_view(
    model=ConnectedEmail,
    create_schema=ConnectedEmailSchemeCreate,
    update_schema=ConnectedEmailSchemeUpdate,
    allowed_actions=ALLOWED_ACTIONS
)



@asynccontextmanager
async def lifespanForAdminPanel(app: FastAPI):
    await admin.initialize()
    yield