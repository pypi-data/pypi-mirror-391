import pytest

from tests.fixtures.agents import AgentFixtures
from verse_sdk import verse


@pytest.mark.e2e
def test_langchain_langfuse_http_export():
    with verse.trace("langchain_e2e") as trace:
        agent = AgentFixtures().create_langchain_agent()
        response = agent.ask_about_friends("Ollie the Owl")
        trace.update(output=response)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_langchain_langfuse_http_export_async():
    with verse.trace("langchain_e2e"):
        agent = AgentFixtures().create_langchain_agent()
        async for _ in agent.tell_story_about_character("Cleo the Cat"):
            pass
