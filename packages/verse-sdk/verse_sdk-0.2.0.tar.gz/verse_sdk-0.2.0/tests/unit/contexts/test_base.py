from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from verse_sdk.contexts.base import BaseContext
from verse_sdk.contexts.types import (
    ContextMetadata,
    ContextType,
    ObservationType,
    Score,
)


class ConcreteContext(BaseContext):
    @property
    def observation_type(self) -> ObservationType:
        return "observation"

    @property
    def type(self) -> ContextType:
        return "span"


class TestBaseContext:
    def setup_method(self):
        self.mock_span = Mock()
        self.mock_span.add_event = Mock()
        self.mock_span.get_span_context.return_value.is_valid = True
        self.mock_span.record_exception = Mock()
        self.mock_span.set_attribute = Mock()
        self.mock_span.set_status = Mock()

    def test_init_with_valid_span(self):
        context = ConcreteContext(self.mock_span)

        assert context._span == self.mock_span
        self.mock_span.set_attribute.assert_any_call("context.type", "span")
        self.mock_span.set_attribute.assert_any_call("observation.type", "observation")

    def test_init_with_invalid_span_raises_error(self):
        invalid_span = Mock()
        invalid_span.get_span_context.return_value.is_valid = False

        with patch("verse_sdk.contexts.base.logging"), pytest.raises(
            ValueError, match="Span invalid"
        ):
            ConcreteContext(invalid_span)

    def test_init_with_none_span_raises_error(self):
        with patch("verse_sdk.contexts.base.logging"), pytest.raises(
            ValueError, match="Span invalid"
        ):
            ConcreteContext(None)

    def test_span_property(self):
        context = ConcreteContext(self.mock_span)
        assert context.span == self.mock_span

    def test_observation_type_property_not_implemented(self):
        class IncompleteContext(BaseContext):
            @property
            def type(self) -> ContextType:
                return "span"

        with pytest.raises(
            NotImplementedError, match="Observation type must be implemented"
        ):
            assert IncompleteContext(self.mock_span).observation_type

    def test_type_property_not_implemented(self):
        class IncompleteContext(BaseContext):
            pass

        with pytest.raises(
            NotImplementedError, match="Context type must be implemented"
        ):
            assert IncompleteContext(self.mock_span).type

    def test_metadata_success(self):
        context = ConcreteContext(self.mock_span)
        metadata: ContextMetadata = {"key1": "value1", "key2": "value2"}

        result = context.metadata(metadata)
        assert result == context
        self.mock_span.set_attribute.assert_any_call("metadata.key1", "value1")
        self.mock_span.set_attribute.assert_any_call("metadata.key2", "value2")

    def test_metadata_with_none_values(self):
        context = ConcreteContext(self.mock_span)
        metadata: ContextMetadata = {"key1": "value1", "key2": None, "key3": "value3"}

        context.metadata(metadata)

        self.mock_span.set_attribute.assert_any_call("metadata.key1", "value1")
        self.mock_span.set_attribute.assert_any_call("metadata.key3", "value3")
        assert not any(
            call[0][0] == "metadata.key2"
            for call in self.mock_span.set_attribute.call_args_list
        )

    def test_error_success(self):
        context = ConcreteContext(self.mock_span)
        exception = ValueError("Test error message")

        result = context.error(exception)

        assert result == context
        self.mock_span.set_attribute.assert_any_call("error", True)
        self.mock_span.set_attribute.assert_any_call("error.type", "ValueError")
        self.mock_span.set_attribute.assert_any_call(
            "error.message", "Test error message"
        )
        self.mock_span.record_exception.assert_called_once_with(exception)
        self.mock_span.set_status.assert_called_once()

    def test_error_with_exception_during_processing(self):
        context = ConcreteContext(self.mock_span)
        exception = ValueError("Test error message")

        self.mock_span.set_attribute.side_effect = Exception("Attribute setting failed")

        with patch("verse_sdk.contexts.base.logging") as mock_logging:
            result = context.error(exception)

            assert result == context
            mock_logging.warning.assert_called_once()

    def test_score_generation_context(self):
        class GenerationContext(BaseContext):
            @property
            def observation_type(self) -> ObservationType:
                return "observation"

            @property
            def type(self) -> ContextType:
                return "generation"

        context = GenerationContext(self.mock_span)
        score: Score = {
            "name": "quality",
            "value": 0.85,
            "comment": "High quality response",
        }

        result = context.score(score)

        assert result == context
        self.mock_span.set_attribute.assert_any_call(
            "generation_score.quality.comment", "High quality response"
        )
        self.mock_span.set_attribute.assert_any_call(
            "generation_score.quality.value", "0.85"
        )
        self.mock_span.add_event.assert_called_once_with(
            "generation_score",
            {
                "name": "quality",
                "value": "0.85",
                "comment": "High quality response",
            },
        )

    def test_score_observation_context(self):
        context = ConcreteContext(self.mock_span)
        score: Score = {
            "name": "relevance",
            "value": "high",
            "comment": "Very relevant",
        }

        result = context.score(score)

        assert result == context
        self.mock_span.set_attribute.assert_any_call(
            "span_score.relevance.comment", "Very relevant"
        )
        self.mock_span.set_attribute.assert_any_call(
            "span_score.relevance.value", "high"
        )

    def test_score_with_exception_during_processing(self):
        context = ConcreteContext(self.mock_span)
        score: Score = {"name": "test", "value": 1.0, "comment": "test comment"}

        self.mock_span.set_attribute.side_effect = Exception("Attribute setting failed")

        with patch("verse_sdk.contexts.base.logging") as mock_logging:
            result = context.score(score)

            assert result == context
            mock_logging.warning.assert_called_once()

    def test_set_attributes_with_prefix(self):
        context = ConcreteContext(self.mock_span)

        result = context.set_attributes("test", key1="value1", key2="value2")

        assert result == context
        self.mock_span.set_attribute.assert_any_call("test.key1", "value1")
        self.mock_span.set_attribute.assert_any_call("test.key2", "value2")

    def test_set_attributes_without_prefix(self):
        context = ConcreteContext(self.mock_span)

        result = context.set_attributes(key1="value1", key2="value2")

        assert result == context
        self.mock_span.set_attribute.assert_any_call("key1", "value1")
        self.mock_span.set_attribute.assert_any_call("key2", "value2")

    def test_set_attributes_filters_none_values(self):
        context = ConcreteContext(self.mock_span)

        context.set_attributes("test", key1="value1", key2=None, key3="value3")

        self.mock_span.set_attribute.assert_any_call("test.key1", "value1")
        self.mock_span.set_attribute.assert_any_call("test.key3", "value3")
        assert not any(
            call[0][0] == "test.key2"
            for call in self.mock_span.set_attribute.call_args_list
        )

    def test_set_attributes_with_exception_during_processing(self):
        context = ConcreteContext(self.mock_span)

        self.mock_span.set_attribute.side_effect = Exception("Attribute setting failed")

        with patch("verse_sdk.contexts.base.logging") as mock_logging:
            result = context.set_attributes(key1="value1")

            assert result == context
            mock_logging.warning.assert_called_once()

    def test_method_chaining(self):
        context = ConcreteContext(self.mock_span)
        metadata: ContextMetadata = {"key": "value"}
        score: Score = {"name": "test", "value": 1.0, "comment": "test"}
        exception = ValueError("test error")

        result = (
            context.metadata(metadata)
            .score(score)
            .error(exception)
            .set_attributes("test", key="value")
        )

        assert result == context

    def test_get_trace_metadata_success(self):
        context = ConcreteContext(self.mock_span)
        mock_span_context = Mock()
        mock_span_context.span_id = 0x1234567890ABCDEF
        mock_span_context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        expected_result = {
            "parent_observation_id": "1234567890abcdef",
            "trace_id": "1234567890abcdef1234567890abcdef",
        }
        assert result == expected_result

    def test_get_trace_metadata_with_zero_ids(self):
        context = ConcreteContext(self.mock_span)
        mock_span_context = Mock()
        mock_span_context.span_id = 0x0
        mock_span_context.trace_id = 0x0
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        expected_result = {
            "parent_observation_id": "0000000000000000",
            "trace_id": "00000000000000000000000000000000",
        }
        assert result == expected_result

    def test_get_trace_metadata_with_max_values(self):
        context = ConcreteContext(self.mock_span)
        mock_span_context = Mock()
        mock_span_context.span_id = 0xFFFFFFFFFFFFFFFF
        mock_span_context.trace_id = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        expected_result = {
            "parent_observation_id": "ffffffffffffffff",
            "trace_id": "ffffffffffffffffffffffffffffffff",
        }
        assert result == expected_result

    def test_get_trace_metadata_hex_formatting(self):
        context = ConcreteContext(self.mock_span)
        mock_span_context = Mock()
        mock_span_context.span_id = 0x1A2B3C4D5E6F7890
        mock_span_context.trace_id = 0x1A2B3C4D5E6F78901A2B3C4D5E6F7890
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        expected_result = {
            "parent_observation_id": "1a2b3c4d5e6f7890",
            "trace_id": "1a2b3c4d5e6f78901a2b3c4d5e6f7890",
        }
        assert result == expected_result

    def test_get_trace_metadata_return_type(self):
        context = ConcreteContext(self.mock_span)

        mock_span_context = Mock()
        mock_span_context.span_id = 0x1234567890ABCDEF
        mock_span_context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        assert isinstance(result, dict)
        assert "parent_observation_id" in result
        assert "trace_id" in result
        assert isinstance(result["parent_observation_id"], str)
        assert isinstance(result["trace_id"], str)

    def test_get_trace_metadata_string_lengths(self):
        context = ConcreteContext(self.mock_span)

        mock_span_context = Mock()
        mock_span_context.span_id = 0x1234567890ABCDEF
        mock_span_context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        assert len(result["parent_observation_id"]) == 16
        assert len(result["trace_id"]) == 32

    def test_get_trace_metadata_hex_strings(self):
        context = ConcreteContext(self.mock_span)

        mock_span_context = Mock()
        mock_span_context.span_id = 0x1234567890ABCDEF
        mock_span_context.trace_id = 0x1234567890ABCDEF1234567890ABCDEF
        self.mock_span.context = mock_span_context

        result = context.get_trace_metadata()

        import re

        hex_pattern = re.compile(r"^[0-9a-f]+$")
        assert hex_pattern.match(result["parent_observation_id"])
        assert hex_pattern.match(result["trace_id"])

    def test_get_trace_metadata_different_contexts(self):
        """Test that different context instances return different metadata"""
        mock_span1 = Mock()
        mock_span1.get_span_context.return_value.is_valid = True
        mock_span_context1 = Mock()
        mock_span_context1.span_id = 0x1111111111111111
        mock_span_context1.trace_id = 0x11111111111111111111111111111111
        mock_span1.context = mock_span_context1

        mock_span2 = Mock()
        mock_span2.get_span_context.return_value.is_valid = True
        mock_span_context2 = Mock()
        mock_span_context2.span_id = 0x2222222222222222
        mock_span_context2.trace_id = 0x22222222222222222222222222222222
        mock_span2.context = mock_span_context2

        context1 = ConcreteContext(mock_span1)
        context2 = ConcreteContext(mock_span2)

        result1 = context1.get_trace_metadata()
        result2 = context2.get_trace_metadata()

        assert result1 != result2
        assert result1["parent_observation_id"] == "1111111111111111"
        assert result1["trace_id"] == "11111111111111111111111111111111"
        assert result2["parent_observation_id"] == "2222222222222222"
        assert result2["trace_id"] == "22222222222222222222222222222222"
