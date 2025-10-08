import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project's root directory to the Python path.
# This allows us to import the 'neogrid' module from within the tests
# regardless of the current working directory.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

from neogrid.backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c