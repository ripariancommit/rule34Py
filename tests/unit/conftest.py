from tests.fixtures import mock34, rule34


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "captcha: marks tests as calling into a captcha-protected endpoint."
    )
