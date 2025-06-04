from pathlib import Path
import os

import responses
import responses._recorder
import pytest

from rule34Py.__vars__ import __base_url__, __api_url__


SCRIPT_ROOT = Path(__file__).parent
REGISTRY_FILE = SCRIPT_ROOT / "responses.yml"


class Mock34():

    def __init__(self, record_responses: bool=False):
        if record_responses:
            self.requests_mock = responses._recorder.Recorder()
        else:
            self.requests_mock = responses.RequestsMock()
        # For some reason, RequestsMock defaults to erroring if it ever dies
        # without all of its registered intercepts firing. Turn off this
        # behavior.
        self.requests_mock.assert_all_requests_are_fired = False
        self._registry = self.requests_mock._registry

    @property
    def is_recorder(self):
        if isinstance(self.requests_mock, responses._recorder.Recorder):
            return True
        else:
            return False
    
    def start(self):
        self.requests_mock.start()
        if REGISTRY_FILE.exists():
            self.requests_mock._add_from_file(REGISTRY_FILE)

    def stop(self):
        if self.is_recorder:
            self.requests_mock.dump_to_file(
                file_path=REGISTRY_FILE,
                registered=self._registry.registered,
            )
        self.requests_mock.stop()
        self.requests_mock.reset()


def str_to_bool(string: str) -> bool:
    """Interpret a string as a boolean value.

    Returns:
        True, if the string value is any integer > 0 or the string literal \"true\" (with any capitalization; False otherwise.)
    """
    try:
        return bool(int(string))
    except ValueError:
        pass

    string = string.lower()
    return string == "true"


@pytest.fixture(scope="session", autouse=True)
def mock34():
    """A fixture for mocking rule34.xxx HTTP requests.
    
    This fixture provides a passive context which intercepts 'requests' module HTTP requests and either (a) responds with recorded http content from the real rule34.xxx or (b) proxies the request to the real site and stores the response for later use.
    
    Which behavior is followed is controlled by the value in the OS's `R34_RECORD_RESPONSES` variable. If python would evaluate that variable as True, then requests are proxied and recorded; otherwise they are replayed.

    If the ``R34_MOCK`` environment variable is set to "False" (or 0), this fixture will disable itself, allowing requests to proceed to the public API unmolested.
    """
    record_responses = str_to_bool(os.environ.get("R34_RECORD_RESPONSES", "False"))
    enable_mock = str_to_bool(os.environ.get("R34_MOCK", "True"))

    if not enable_mock:
        yield None
        return

    mock_service = Mock34(record_responses)
    mock_service.start()
    with mock_service.requests_mock as request_mock:
        yield request_mock
    mock_service.stop()
