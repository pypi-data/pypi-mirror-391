import pytest

from tests.fixtures.agents import AgentFixtures
from verse_sdk import get_current_trace_context, observe, verse


@pytest.mark.e2e
def test_litellm_langfuse_http_export():
    @observe("litellm_e2e", type="trace")
    def agent_completition():
        agent = AgentFixtures().create_litellm_agent()
        resp = agent.ask_about_friends("Ollie the Owl")
        trace = get_current_trace_context()
        trace.update(output=resp)

    agent_completition()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_litellm_langfuse_http_export_async():
    with verse.trace("litellm_e2e"):
        agent = AgentFixtures().create_litellm_agent()
        async for _ in agent.tell_story_about_character("Cleo the Cat"):
            pass
