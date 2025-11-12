import pytest

from tests.fixtures.agents import AgentFixtures
from verse_sdk import get_current_trace_context, observe


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_pydantic_ai_verse_http_export():
    @observe("pydantic_ai_e2e", type="trace")
    async def agent_completition():
        get_current_trace_context().user("test-user-123")
        agent = AgentFixtures().create_pydantic_agent()
        response = await agent.ask_about_friends("Ollie the Owl")
        return response

    await agent_completition()
