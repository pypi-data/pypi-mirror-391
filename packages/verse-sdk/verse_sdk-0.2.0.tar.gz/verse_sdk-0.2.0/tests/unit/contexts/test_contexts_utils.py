from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from opentelemetry.trace import SpanKind

from verse_sdk.contexts.utils import create_span_in_existing_trace


class TestCreateSpanInExistingTrace:
    def test_create_span_with_valid_hex_strings(self):
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_trace.get_tracer.assert_called_once()
            mock_tracer.start_span.assert_called_once_with(
                "llm_generation",
                context=mock_trace.set_span_in_context.return_value,
                kind=SpanKind.INTERNAL,
            )

    def test_create_span_with_hex_prefixes(self):
        trace_id_hex = "0x1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "0X1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_tracer.start_span.assert_called_once()

    def test_create_span_with_non_string_inputs(self):
        trace_id_hex = 0x1234567890ABCDEF1234567890ABCDEF
        parent_span_id_hex = 0x1234567890ABCDEF

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_tracer.start_span.assert_called_once()

    def test_create_span_with_zero_values(self):
        trace_id_hex = "00000000000000000000000000000000"
        parent_span_id_hex = "0000000000000000"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_tracer.start_span.assert_called_once()

    def test_create_span_with_max_values(self):
        trace_id_hex = "ffffffffffffffffffffffffffffffff"
        parent_span_id_hex = "ffffffffffffffff"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_tracer.start_span.assert_called_once()

    def test_create_span_span_context_creation(self):
        """Test that SpanContext is created with correct parameters"""
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace, patch(
            "verse_sdk.contexts.utils.SpanContext"
        ) as mock_span_context_class, patch(
            "verse_sdk.contexts.utils.TraceFlags"
        ) as mock_trace_flags_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            mock_span_context = Mock()
            mock_span_context_class.return_value = mock_span_context

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            # Verify SpanContext was created with correct parameters
            expected_trace_id = int(trace_id_hex, 16)
            expected_span_id = int(parent_span_id_hex, 16)

            mock_span_context_class.assert_called_once_with(
                trace_id=expected_trace_id,
                span_id=expected_span_id,
                is_remote=True,
                trace_flags=mock_trace_flags_class.return_value,
            )

    def test_create_span_trace_flags_setting(self):
        """Test that TraceFlags is set correctly"""
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace, patch(
            "verse_sdk.contexts.utils.TraceFlags"
        ) as mock_trace_flags_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            # Verify TraceFlags was created with correct value
            mock_trace_flags_class.assert_called_once_with(0x01)

    def test_create_span_non_recording_span_creation(self):
        """Test that NonRecordingSpan is created correctly"""
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace, patch(
            "verse_sdk.contexts.utils.SpanContext"
        ) as mock_span_context_class:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            mock_span_context = Mock()
            mock_span_context_class.return_value = mock_span_context

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            # Verify NonRecordingSpan was created
            mock_trace.NonRecordingSpan.assert_called_once_with(mock_span_context)

    def test_create_span_context_setting(self):
        """Test that span context is set correctly"""
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            mock_parent_span = Mock()
            mock_trace.NonRecordingSpan.return_value = mock_parent_span

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            # Verify set_span_in_context was called
            mock_trace.set_span_in_context.assert_called_once_with(mock_parent_span)

    def test_create_span_with_invalid_hex_raises_error(self):
        trace_id_hex = "invalid_hex_string"
        parent_span_id_hex = "1234567890abcdef"

        with pytest.raises(
            ValueError, match="invalid literal for int\\(\\) with base 16"
        ):
            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

    def test_create_span_with_empty_strings_raises_error(self):
        trace_id_hex = ""
        parent_span_id_hex = ""

        with pytest.raises(
            ValueError, match="invalid literal for int\\(\\) with base 16"
        ):
            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

    def test_create_span_with_none_inputs_raises_error(self):
        with pytest.raises(
            ValueError, match="invalid literal for int\\(\\) with base 16: 'None'"
        ):
            create_span_in_existing_trace(None, None)

    def test_create_span_span_kind_is_internal(self):
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            call_args = mock_tracer.start_span.call_args
            assert call_args[1]["kind"] == SpanKind.INTERNAL

    def test_create_span_name_is_llm_generation(self):
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            call_args = mock_tracer.start_span.call_args
            assert call_args[0][0] == "llm_generation"

    def test_create_span_with_mixed_case_hex_prefixes(self):
        trace_id_hex = "0X1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "0x1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            mock_tracer.start_span.assert_called_once()

    def test_create_span_hex_conversion_edge_cases(self):
        test_cases = [
            ("0x0", "0x0"),
            ("0X0", "0X0"),
            ("0", "0"),
            ("1", "1"),
            ("a", "b"),
        ]

        for trace_id, parent_span_id in test_cases:
            with patch("verse_sdk.contexts.utils.trace") as mock_trace:
                mock_tracer = Mock()
                mock_span = Mock()
                mock_trace.get_tracer.return_value = mock_tracer
                mock_tracer.start_span.return_value = mock_span

                result = create_span_in_existing_trace(trace_id, parent_span_id)

                assert result == mock_span
                mock_tracer.start_span.assert_called_once()

    def test_create_span_return_type(self):
        trace_id_hex = "1234567890abcdef1234567890abcdef"
        parent_span_id_hex = "1234567890abcdef"

        with patch("verse_sdk.contexts.utils.trace") as mock_trace:
            mock_tracer = Mock()
            mock_span = Mock()
            mock_trace.get_tracer.return_value = mock_tracer
            mock_tracer.start_span.return_value = mock_span

            result = create_span_in_existing_trace(trace_id_hex, parent_span_id_hex)

            assert result == mock_span
            assert hasattr(result, "__class__")
