from __future__ import annotations

import inspect
import logging
from contextlib import contextmanager
from functools import wraps

from .contexts import ContextType, OperationType
from .sdk import VerseSDK
from .utils import to_json


def create_decorator(sdk: VerseSDK) -> VerseSDK:
    def observe_wrapper(
        name: str | None = None,
        type: ContextType = "span",
        capture_input: bool = True,
        capture_metadata: bool = True,
        capture_output: bool = True,
        operation_type: OperationType | None = None,
        **attrs,
    ):
        """
        Context decorator for any arbitrary function.

        Parameters:
            - name: str | None
                The name of the observation.
            - type: ContextType
                The type of the observation.
            - capture_input: bool
                Whether to capture the input of the function.
            - capture_metadata: bool
                Whether to capture the metadata of the function.
            - capture_output: bool
                Whether to capture the output of the function.
            - operation_type: OperationType | None
                The type of the operation.
            - attrs: dict
                Additional attributes to set on the observation.

        Returns:
            A decorator function.
        """

        def decorator(fn):
            def _exec_capture_input_and_metadata(observation, args, kwargs):
                if capture_input:
                    observation.input(to_json({"args": args, "kwargs": kwargs}))

                if capture_metadata and "metadata" in kwargs:
                    observation.metadata(metadata=kwargs["metadata"])

                observation.set_attributes(**attrs)

            def _exec_capture_output(observation, result):
                if capture_output:
                    observation.output(to_json(result))

            @contextmanager
            def _get_observation():
                observation_method = getattr(sdk, type)
                observation_name = name or fn.__name__
                with observation_method(observation_name, **attrs) as observation:
                    yield observation

            @wraps(fn)
            def _observer(*args, **kwargs):
                try:
                    with _get_observation() as observation:
                        _exec_capture_input_and_metadata(observation, args, kwargs)

                        try:
                            result = fn(*args, **kwargs)
                            _exec_capture_output(observation, result)
                            return result
                        except Exception as e:
                            observation.error(e)
                            raise e
                except Exception as e:
                    logging.warning(
                        f"Failed to instrument function '{fn.__name__}'",
                        exc_info=e,
                    )

                    return fn(*args, **kwargs)

            @wraps(fn)
            async def _observer_async(*args, **kwargs):
                try:
                    with _get_observation() as observation:
                        _exec_capture_input_and_metadata(observation, args, kwargs)

                        try:
                            result = await fn(*args, **kwargs)
                            _exec_capture_output(observation, result)
                            return result
                        except Exception as e:
                            observation.error(e)
                            raise e
                except Exception as e:
                    logging.warning(
                        f"Failed to instrument async function '{fn.__name__}'",
                        exc_info=e,
                    )

                    return fn(*args, **kwargs)

            def _set_op():
                if type == "span" and operation_type:
                    attrs["op"] = operation_type
                elif type == "tool":
                    attrs["op"] = "tool"

            _set_op()
            return _observer_async if inspect.iscoroutinefunction(fn) else _observer

        return decorator

    return observe_wrapper
