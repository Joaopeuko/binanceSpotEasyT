import pytest


def pytest_addoption(parser):
    parser.addoption("--environment", action="store", choices=("local", "actions"), default="actions")


@pytest.fixture(scope="session")
def get_environment(pytestconfig):
    return pytestconfig.getoption("environment")


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        pass
