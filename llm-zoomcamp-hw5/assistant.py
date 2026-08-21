import os

from dotenv import load_dotenv
from openai import OpenAI

from ingest import load_faq_data, build_index
from metrics import RAGWithMetrics
from db_save import save_conversation


def create_assistant():
    load_dotenv()

    documents = load_faq_data()
    index = build_index(documents)

    llm_client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    return RAGWithMetrics(
        index=index,
        llm_client=llm_client
    )


if __name__ == "__main__":
    import sys

    query = sys.argv[1]

    assistant = create_assistant()

    answer = assistant.rag(query)

    print(answer)

    save_conversation(
        assistant.last_call,
        query,
        "llm-zoomcamp"
    )