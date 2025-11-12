from unittest.mock import Mock

from verse_sdk.integrations.litellm.utils import (
    calculate_total_tokens,
    get_completition_choices,
    get_finish_reason,
    get_operation_type,
    get_stream_text,
    get_trace_metadata,
    get_usage,
    get_usage_from_response,
)


class TestCalculateTotalTokens:
    def test_both_tokens_provided(self):
        assert calculate_total_tokens(100, 50) == 150

    def test_only_prompt_tokens(self):
        assert calculate_total_tokens(100, None) == 100

    def test_only_completion_tokens(self):
        assert calculate_total_tokens(None, 50) == 50

    def test_both_none(self):
        assert calculate_total_tokens(None, None) is None

    def test_zero_tokens(self):
        assert (
            calculate_total_tokens(0, 0)
            == calculate_total_tokens(0, None)
            == calculate_total_tokens(None, 0)
            == 0
        )


class TestGetCompletionChoices:
    def test_object_with_choices_attribute(self):
        mock_data = Mock()
        mock_data.choices = [{"message": "test1"}, {"message": "test2"}]
        assert get_completition_choices(mock_data) == mock_data.choices

    def test_dict_with_choices_key(self):
        data = {"choices": [{"message": "test1"}, {"message": "test2"}]}
        assert get_completition_choices(data) == [
            {"message": "test1"},
            {"message": "test2"},
        ]

    def test_empty_choices_list(self):
        mock_data = Mock()
        mock_data.choices = []
        assert get_completition_choices(mock_data) == []

    def test_no_choices_attribute_or_key(self):
        mock_data = Mock()
        del mock_data.choices
        assert get_completition_choices(mock_data) == []

    def test_dict_without_choices_key(self):
        data = {"other_key": "value"}
        assert get_completition_choices(data) == []

    def test_none_data(self):
        assert get_completition_choices(None) == []

    def test_string_data(self):
        assert get_completition_choices("some string") == []


class TestGetFinishReason:
    def test_response_with_choices_and_finish_reason(self):
        mock_choice = Mock()
        mock_choice.finish_reason = "stop"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_finish_reason(mock_response) == "stop"

    def test_response_with_choices_no_finish_reason(self):
        mock_choice = Mock()
        del mock_choice.finish_reason

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_finish_reason(mock_response) is None

    def test_response_without_choices(self):
        mock_response = Mock()
        del mock_response.choices
        assert get_finish_reason(mock_response) is None

    def test_response_choices_is_none(self):
        mock_response = Mock()
        mock_response.choices = None
        assert get_finish_reason(mock_response) is None

    def test_response_choices_is_empty_list(self):
        mock_response = Mock()
        mock_response.choices = []
        assert get_finish_reason(mock_response) is None

    def test_none_response(self):
        assert get_finish_reason(None) is None


class TestGetOperationType:
    def test_embedding_operation(self):
        messages = []
        kwargs = {"litellm_params": {"api_base": "https://api.example.com/embeddings"}}
        assert get_operation_type(messages, kwargs) == "embedding"

    def test_chat_operation_with_messages(self):
        messages = [{"role": "user", "content": "Hello"}]
        kwargs = {}
        assert get_operation_type(messages, kwargs) == "chat"

    def test_completion_operation_no_messages(self):
        messages = []
        kwargs = {}
        assert get_operation_type(messages, kwargs) == "completion"

    def test_completion_operation_none_messages(self):
        messages = None
        kwargs = {}
        assert get_operation_type(messages, kwargs) == "completion"

    def test_embedding_operation_with_messages(self):
        messages = [{"role": "user", "content": "Hello"}]
        kwargs = {"litellm_params": {"api_base": "https://api.example.com/embeddings"}}
        assert get_operation_type(messages, kwargs) == "embedding"

    def test_embedding_operation_partial_url(self):
        messages = []
        kwargs = {"litellm_params": {"api_base": "/embeddings"}}
        assert get_operation_type(messages, kwargs) == "embedding"

    def test_exception_handling(self):
        messages = []
        kwargs = {"invalid": object()}
        assert get_operation_type(messages, kwargs) == "completion"


class TestGetStreamText:
    def test_response_with_delta_content(self):
        mock_delta = Mock()
        mock_delta.content = "streamed text"

        mock_choice = Mock()
        mock_choice.delta = mock_delta
        del mock_choice.text

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_stream_text(mock_response) == "streamed text"

    def test_response_with_text_attribute(self):
        mock_choice = Mock()
        del mock_choice.delta
        mock_choice.text = "completion text"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_stream_text(mock_response) == "completion text"

    def test_response_with_both_delta_and_text(self):
        mock_delta = Mock()
        mock_delta.content = "streamed text"

        mock_choice = Mock()
        mock_choice.delta = mock_delta
        mock_choice.text = "completion text"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_stream_text(mock_response) == "streamed text"

    def test_response_with_none_delta_content(self):
        mock_delta = Mock()
        mock_delta.content = None

        mock_choice = Mock()
        mock_choice.delta = mock_delta
        mock_choice.text = "completion text"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        assert get_stream_text(mock_response) == "completion text"

    def test_response_with_no_choices(self):
        mock_response = Mock()
        mock_response.choices = None
        assert get_stream_text(mock_response) == ""

    def test_response_with_empty_choices(self):
        mock_response = Mock()
        mock_response.choices = []
        assert get_stream_text(mock_response) == ""

    def test_response_with_none_choices(self):
        mock_response = Mock()
        del mock_response.choices
        assert get_stream_text(mock_response) == ""

    def test_none_response(self):
        assert get_stream_text(None) == ""


class TestGetUsage:
    def test_basic_kwargs(self):
        kwargs = {"max_tokens": 100, "temperature": 0.7, "top_p": 0.9, "stream": True}
        assert get_usage(kwargs) == {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": True,
        }

    def test_optional_params_fallback(self):
        kwargs = {
            "max_tokens": 100,
            "temperature": 0.7,
            "optional_params": {
                "max_tokens": 200,
                "temperature": 0.8,
                "top_p": 0.95,
                "stream": False,
            },
        }

        assert get_usage(kwargs) == {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.95,
            "stream": False,
        }

    def test_mixed_kwargs_and_optional_params(self):
        kwargs = {
            "max_tokens": 100,
            "temperature": 0.7,
            "optional_params": {"top_p": 0.95, "stream": False},
        }

        assert get_usage(kwargs) == {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.95,
            "stream": False,
        }

    def test_missing_keys(self):
        kwargs = {"max_tokens": 100, "optional_params": {"temperature": 0.8}}

        assert get_usage(kwargs) == {
            "max_tokens": 100,
            "temperature": 0.8,
            "top_p": None,
            "stream": None,
        }

    def test_empty_kwargs(self):
        kwargs = {}

        assert get_usage(kwargs) == {
            "max_tokens": None,
            "temperature": None,
            "top_p": None,
            "stream": None,
        }

    def test_none_optional_params(self):
        kwargs = {"max_tokens": 100, "optional_params": None}
        assert get_usage(kwargs) == {}

    def test_exception_handling(self):
        kwargs = {"invalid": object()}

        assert get_usage(kwargs) == {
            "max_tokens": None,
            "temperature": None,
            "top_p": None,
            "stream": None,
        }


class TestGetUsageFromResponse:
    def test_response_with_usage_object(self):
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        mock_usage.total_tokens = 150

        mock_response = Mock()
        mock_response.usage = mock_usage
        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

    def test_response_with_usage_object_no_total_tokens(self):
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        del mock_usage.total_tokens

        mock_response = Mock()
        mock_response.usage = mock_usage
        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

    def test_response_with_usage_object_partial_tokens(self):
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        del mock_usage.completion_tokens
        del mock_usage.total_tokens

        mock_response = Mock()
        mock_response.usage = mock_usage

        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": 100,
            "completion_tokens": None,
            "total_tokens": 100,
        }

    def test_response_with_usage_object_none_tokens(self):
        mock_usage = Mock()
        mock_usage.prompt_tokens = None
        mock_usage.completion_tokens = None
        del mock_usage.total_tokens

        mock_response = Mock()
        mock_response.usage = mock_usage

        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    def test_response_without_usage_attribute(self):
        mock_response = Mock()
        del mock_response.usage

        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    def test_response_with_none_usage(self):
        mock_response = Mock()
        mock_response.usage = None

        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    def test_none_response(self):
        assert get_usage_from_response(None) == {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    def test_exception_handling(self):
        mock_response = Mock()
        mock_response.usage = object()
        assert get_usage_from_response(mock_response) == {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }


class TestGetTraceMetadata:
    def test_both_trace_id_and_parent_observation_id(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": "trace-123",
                    "parent_observation_id": "obs-456",
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": "obs-456",
            "trace_id": "trace-123",
        }

    def test_only_trace_id(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": "trace-123",
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": "trace-123",
        }

    def test_only_parent_observation_id(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "parent_observation_id": "obs-456",
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": "obs-456",
            "trace_id": None,
        }

    def test_empty_metadata(self):
        kwargs = {"litellm_params": {"metadata": {}}}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_no_metadata_key(self):
        kwargs = {"litellm_params": {}}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_no_litellm_params(self):
        kwargs = {}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_none_litellm_params(self):
        kwargs = {"litellm_params": None}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_none_metadata(self):
        kwargs = {"litellm_params": {"metadata": None}}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_empty_kwargs(self):
        kwargs = {}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_none_kwargs(self):
        assert get_trace_metadata(None) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_metadata_with_extra_keys(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": "trace-123",
                    "parent_observation_id": "obs-456",
                    "extra_key": "extra_value",
                    "another_key": "another_value",
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": "obs-456",
            "trace_id": "trace-123",
        }

    def test_string_values(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": "string-trace-id",
                    "parent_observation_id": "string-obs-id",
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": "string-obs-id",
            "trace_id": "string-trace-id",
        }

    def test_numeric_values(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": 12345,
                    "parent_observation_id": 67890,
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": 67890,
            "trace_id": 12345,
        }

    def test_boolean_values(self):
        kwargs = {
            "litellm_params": {
                "metadata": {
                    "trace_id": True,
                    "parent_observation_id": False,
                }
            }
        }
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": False,
            "trace_id": True,
        }

    def test_exception_handling_invalid_structure(self):
        kwargs = {"litellm_params": {"metadata": object()}}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }

    def test_exception_handling_invalid_kwargs(self):
        kwargs = {"invalid": object()}
        assert get_trace_metadata(kwargs) == {
            "parent_observation_id": None,
            "trace_id": None,
        }


class TestIntegrationScenarios:
    def test_calculate_total_tokens_integration(self):
        mock_usage = Mock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        del mock_usage.total_tokens

        mock_response = Mock()
        mock_response.usage = mock_usage

        assert get_usage_from_response(mock_response)["total_tokens"] == 150

    def test_get_operation_type_with_embedding_url_variations(self):
        test_cases = [
            ("https://api.openai.com/v1/embeddings", "embedding"),
            ("http://localhost:8000/embeddings", "embedding"),
            ("/embeddings", "embedding"),
            ("embeddings", "completion"),
            ("https://api.openai.com/v1/chat/completions", "completion"),
            ("", "completion"),
        ]

        for api_base, expected in test_cases:
            kwargs = {"litellm_params": {"api_base": api_base}}
            result = get_operation_type([], kwargs)
            assert result == expected, f"Failed for api_base: {api_base}"

    def test_get_stream_text_with_various_chunk_formats(self):
        mock_delta = Mock()
        mock_delta.content = "Hello"

        mock_choice = Mock()
        mock_choice.delta = mock_delta
        del mock_choice.text

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        result = get_stream_text(mock_response)
        assert result == "Hello"

        mock_choice2 = Mock()
        del mock_choice2.delta
        mock_choice2.text = "World"

        mock_response2 = Mock()
        mock_response2.choices = [mock_choice2]

        result2 = get_stream_text(mock_response2)
        assert result2 == "World"
