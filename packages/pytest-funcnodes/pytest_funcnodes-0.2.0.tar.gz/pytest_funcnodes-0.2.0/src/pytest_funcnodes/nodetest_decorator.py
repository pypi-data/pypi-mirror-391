from typing import Callable, List, Union, Type
import funcnodes_core as fn
import functools
import pytest


def nodetest(node: Union[None, List[Type[fn.Node]], Type[fn.Node]] = None):
    """Decorator for async node tests.
    This decorator automatically applies:
    - The 'nodetest' marker, so that tests can be filtered via --nodetests-only.
    - The 'pytest.mark.asyncio' marker so that the test is run in an async event loop.
    """

    if node is None:
        node = []
    elif not isinstance(node, list):
        node = [node]

    if not all(issubclass(n, fn.Node) for n in node):
        raise TypeError("node must be a subclass of funcnodes_core.Node")

    def decorator(func):
        @pytest.mark.nodetest(nodes=node)
        @pytest.mark.asyncio(loop_scope="function")
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Optionally, you could add common setup/teardown or logging here.
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def funcnodes_test(func: Callable):
    """Decorator for async node tests.
    This decorator automatically applies:
    - The 'nodetest' marker, so that tests can be filtered via --nodetests-only.
    - The 'pytest.mark.asyncio' marker so that the test is run in an async event loop.
    """

    @pytest.mark.funcnodes_test()
    @pytest.mark.asyncio(loop_scope="function")
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Optionally, you could add common setup/teardown or logging here.
        return await func(*args, **kwargs)

    return wrapper
