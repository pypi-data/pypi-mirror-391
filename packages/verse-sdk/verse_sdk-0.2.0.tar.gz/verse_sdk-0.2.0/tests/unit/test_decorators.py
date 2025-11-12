from unittest.mock import Mock, patch

import pytest

from verse_sdk.decorators import create_decorator


class TestDecorators:
    def setup_method(self):
        self.mock_sdk = Mock()
        self.mock_observation = Mock()
        self.mock_sdk.generation.return_value.__enter__ = Mock(
            return_value=self.mock_observation
        )
        self.mock_sdk.generation.return_value.__exit__ = Mock(return_value=None)
        self.mock_sdk.span.return_value.__enter__ = Mock(
            return_value=self.mock_observation
        )
        self.mock_sdk.span.return_value.__exit__ = Mock(return_value=None)
        self.mock_sdk.trace.return_value.__enter__ = Mock(
            return_value=self.mock_observation
        )
        self.mock_sdk.trace.return_value.__exit__ = Mock(return_value=None)
        self.mock_sdk.tool.return_value.__enter__ = Mock(
            return_value=self.mock_observation
        )
        self.mock_sdk.tool.return_value.__exit__ = Mock(return_value=None)

        self.observe = create_decorator(self.mock_sdk)

    def test_observe_generation_decorator(self):
        @self.observe(type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_observe_span_decorator(self):
        @self.observe(type="span")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.span.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_observe_trace_decorator(self):
        @self.observe(type="trace")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.trace.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_with_custom_name(self):
        @self.observe(name="custom_name", type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("custom_name")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_with_attrs(self):
        @self.observe(custom_attr="value", type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with(
            "test_func", custom_attr="value"
        )
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once_with(
            custom_attr="value"
        )

    def test_decorator_capture_input_false(self):
        @self.observe(capture_input=False, type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_not_called()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_capture_output_false(self):
        @self.observe(capture_output=False, type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_not_called()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_capture_metadata_false(self):
        @self.observe(capture_metadata=False, type="generation")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.metadata.assert_not_called()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_with_metadata_kwarg(self):
        @self.observe(type="generation")
        def test_func(metadata=None):
            return "test_result"

        result = test_func(metadata={"key": "value"})
        assert result == "test_result"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.metadata.assert_called_once_with(
            metadata={"key": "value"}
        )
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_preserves_function_metadata(self):
        @self.observe(type="generation")
        def test_func():
            """Test function docstring."""
            return "test_result"

        result = test_func()
        assert result == "test_result"
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_decorator_handles_exception(self):
        @self.observe(type="generation")
        def test_func():
            raise ValueError("Test error")

        with patch("verse_sdk.decorators.logging"), pytest.raises(
            ValueError, match="Test error"
        ):
            test_func()

        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.error.assert_called_once()

    def test_decorator_handles_sdk_exception(self):
        self.mock_sdk.generation.side_effect = Exception("SDK error")

        @self.observe(type="generation")
        def test_func():
            return "test_result"

        with patch("verse_sdk.decorators.logging") as mock_logging:
            result = test_func()
            assert result == "test_result"
            mock_logging.warning.assert_called_once()

    def test_decorator_with_args_and_kwargs(self):
        @self.observe(type="generation")
        def test_func(arg1, arg2, kwarg1=None):
            return f"{arg1}_{arg2}_{kwarg1}"

        result = test_func("a", "b", kwarg1="c")
        assert result == "a_b_c"
        self.mock_sdk.generation.assert_called_once_with("test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    def test_observe_tool_decorator(self):
        @self.observe(type="tool")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.tool.assert_called_once_with("test_func", op="tool")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once_with(op="tool")

    def test_observe_tool_decorator_with_custom_attrs(self):
        @self.observe(custom_attr="value", type="tool")
        def test_func():
            return "test_result"

        result = test_func()
        assert result == "test_result"
        self.mock_sdk.tool.assert_called_once_with(
            "test_func", op="tool", custom_attr="value"
        )
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once_with(
            op="tool", custom_attr="value"
        )

    @pytest.mark.asyncio
    async def test_observe_async_function(self):
        @self.observe()
        async def async_test_func():
            return "async_result"

        result = await async_test_func()
        assert result == "async_result"
        self.mock_sdk.span.assert_called_once_with("async_test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()

    @pytest.mark.asyncio
    async def test_observe_async_function_with_args(self):
        @self.observe(type="generation")
        async def async_test_func(arg1, arg2):
            return f"{arg1}_{arg2}"

        result = await async_test_func("hello", "world")
        assert result == "hello_world"
        self.mock_sdk.generation.assert_called_once_with("async_test_func")
        self.mock_observation.input.assert_called_once()
        self.mock_observation.output.assert_called_once()
        self.mock_observation.set_attributes.assert_called_once()
