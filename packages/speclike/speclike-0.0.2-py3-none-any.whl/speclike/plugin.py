def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "speclike(*labels): structured test classification labels for speclike-based tests"
    )