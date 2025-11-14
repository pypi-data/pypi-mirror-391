import pytest
from .testingsystem import test_context


def pytest_addoption(parser):
    group = parser.getgroup("funcnodes-pytest", "Plugin for tesing Funcnodes-Nodes")
    group.addoption(
        "--nodetests-only",
        action="store_true",
        help="Run only tests marked as nodetest",
    )


def pytest_collection_modifyitems(session: pytest.Session, config, items):
    if config.getoption("--nodetests-only"):
        selected = []
        deselected = []
        for item in items:
            if "nodetest" in item.keywords:
                selected.append(item)
            else:
                deselected.append(item)

        if deselected:
            config.hook.pytest_deselected(items=deselected)

        items[:] = selected

    # Add a custom session attribute
    session.tested_nodes = set()

    for item in items:
        if "nodetest" in item.keywords:
            # get marger argument
            marker = item.get_closest_marker("nodetest")
            nodes = marker.kwargs.get("nodes")
            if nodes is None:
                continue
            session.tested_nodes.update(nodes)


def pytest_configure(config: pytest.Config):
    config.addinivalue_line("markers", "nodetest: mark test as an async node test")
    config.addinivalue_line(
        "markers", "funcnodes_test: mark test as an async funcnodes test"
    )


@pytest.fixture(scope="session", autouse=True)
def all_nodes(request):
    return request.session.tested_nodes


@pytest.fixture(scope="session", autouse=True)
def my_session_fixture():
    # Setup code executed once per session
    print("Session fixture setup")
    yield
    # Teardown code executed once after all tests complete
    print("Session fixture teardown")


@pytest.fixture(autouse=True)
def nodetest_setup_teardown(request):
    marker = request.node.get_closest_marker("nodetest")
    if marker:
        # Code to run before the test function
        with test_context():
            yield
    else:
        yield


@pytest.fixture(autouse=True)
def funcnodes_test_setup_teardown(request):
    marker = request.node.get_closest_marker("funcnodes_test")
    if marker:
        # Code to run before the test function
        with test_context():
            yield
    else:
        yield
