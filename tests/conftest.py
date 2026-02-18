import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from main import app
from api.db import engine


@pytest.fixture(name="client")
def fixture_client():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as client:
        yield client

