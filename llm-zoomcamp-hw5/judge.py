import os
from typing import Literal

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


class RelevanceVerdict(BaseModel):
    relevance: Literal[
        "NON_RELEVANT",
        "PARTLY_RELEVANT",
        "RELEVANT"
    ]
    explanation: str


judge_instructions = """
You are an expert evaluator for a RAG system.
Analyze the relevance of the generated answer to the given question.

Classify the answer as:
- RELEVANT: the answer addresses the question
- PARTLY_RELEVANT: the answer partially addresses the question
- NON_RELEVANT: the answer does not address the question

Return your evaluation as JSON with exactly these fields:
- relevance
- explanation
""".strip()


judge_prompt = """
Question: {question}

Generated Answer: {answer}
""".strip()


def evaluate_relevance(question, answer, client=None):
    if client is None:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = judge_prompt.format(
        question=question,
        answer=answer
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", 
        messages=[
            {
                "role": "system",
                "content": judge_instructions
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0
    )

    result = RelevanceVerdict.model_validate_json(
        response.choices[0].message.content
    )

    return result.relevance, result.explanation


if __name__ == "__main__":
    load_dotenv()

    question = "Can I still join the course?"
    answer = "Yes, you can still join. The course is self-paced."

    relevance, explanation = evaluate_relevance(
        question,
        answer
    )

    print(relevance)
    print(explanation)