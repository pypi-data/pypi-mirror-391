import os

from dotenv import load_dotenv

from verse_sdk import VerseConfig, verse

load_dotenv()


verse.init(
    app_name="verse_pydantic_ai_e2e",
    environment="development",
    exporters=[
        verse.exporters.verse(
            VerseConfig(
                # Using manual config so that project is hardcoded
                api_key=os.environ.get("VERSE_API_KEY"),
                host=os.environ.get("VERSE_HOST"),
                project_id="proj_test123",
            )
        )
    ],
    vendor="pydantic_ai",
    version="1.0.0",
)
