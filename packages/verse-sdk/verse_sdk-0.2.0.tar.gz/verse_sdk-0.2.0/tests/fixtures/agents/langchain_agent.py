from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from tests.fixtures.agents.prompt import SYSTEM_PROMPT
from verse_sdk import verse


class LangchainAgent:
    def __init__(self):
        """Prepare reusable prompt chains for LangChain interactions."""
        self._model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self._streaming_model = ChatOpenAI(
            model="gpt-4o-mini", temperature=0, streaming=True
        )

        self._friends_chain = (
            ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    ("human", "What are {character_name}'s friends?"),
                ]
            )
            | self._model
            | StrOutputParser()
        )

        self._story_chain = (
            ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    (
                        "human",
                        """
                        Tell me a story about the day in the life of {character_name}.
                        Include details about their friends, their job, and the town they live in.
                        """.strip(),
                    ),
                ]
            )
            | self._streaming_model
            | StrOutputParser()
        )

    def ask_about_friends(self, character_name: str) -> str:
        """
        Ask the chain about a character's friends while capturing the interaction in Verse.
        """
        prompt_input = f"What are {character_name}'s friends?"

        with verse.span(
            "Character Friends LC Agent",
            op="agent",
            input=prompt_input,
            scope="test_agent",
        ) as span:
            result = self._friends_chain.invoke({"character_name": character_name})
            span.output(output=result)
            return result

    async def tell_story_about_character(self, character_name: str):
        """
        Stream a story about a character, yielding partial results as the LLM responds.
        """
        prompt_input = (
            f"Tell me a story about the day in the life of {character_name}. "
            "Include details about their friends, their job, and their town."
        )

        with verse.span(
            "Character Story LC Agent",
            op="agent",
            input=prompt_input,
            scope="test_agent",
        ) as span:
            output = ""
            async for chunk in self._story_chain.astream({"character_name": character_name}):
                output += chunk
                yield chunk

            span.output(output=output)
