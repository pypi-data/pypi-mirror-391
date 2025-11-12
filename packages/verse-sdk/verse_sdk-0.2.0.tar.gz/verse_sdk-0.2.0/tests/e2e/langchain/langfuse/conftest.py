from dotenv import load_dotenv

from verse_sdk import verse

load_dotenv()


verse.init(
    app_name="verse_langfuse_langchain_e2e",
    environment="development",
    exporters=[verse.exporters.langfuse()],
    vendor="langchain",
    version="1.0.0",
)
