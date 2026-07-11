import json
import time

from tqdm.auto import tqdm
from rag_helper import RAGBase


# -------------------------------------------------------------------
#V
# -------------------------------------------------------------------

def calc_price(usage):
    input_price_per_million = 0.0
    output_price_per_million = 0.0

    input_cost = (usage.prompt_tokens / 1_000_000) * input_price_per_million
    output_cost = (usage.completion_tokens / 1_000_000) * output_price_per_million

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost,
    }


def calc_total_price(usages):
    total = 0

    for usage in usages:
        total += calc_price(usage)["total_cost"]

    return total


# -------------------------------------------------------------------
# Structured Output for Groq
# -------------------------------------------------------------------

def llm_structured(
    client,
    instructions,
    user_prompt,
    output_type=None,
    model="llama-3.3-70b-versatile"
):

    system_prompt = instructions + """

Return ONLY valid JSON.

Do not use markdown.

Do not write ```json.

"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    text = response.choices[0].message.content

    result = json.loads(text)

    return result, response.usage


def llm_structured_retry(
    client,
    instructions,
    user_prompt,
    output_type=None,
    model="llama-3.3-70b-versatile",
    max_retries=3,
):

    for attempt in range(max_retries):

        try:

            return llm_structured(
                client,
                instructions,
                user_prompt,
                output_type,
                model=model
            )

        except Exception:

            if attempt == max_retries - 1:
                raise

            time.sleep(2 ** attempt)


# -------------------------------------------------------------------
# RAG
# -------------------------------------------------------------------

class RAGWithUsage(RAGBase):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.usages = []

        self.last_usage = None


    def reset_usage(self):

        self.usages = []

        self.last_usage = None


    def search(self, query, num_results=5):

        boost_dict = {
            "question": 1.0,
            "answer": 2.0,
            "section": 0.1
        }

        filter_dict = {
            "course": self.course
        }

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )


    def llm(self, prompt):

        messages = [
            {
                "role": "system",
                "content": self.instructions
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        self.last_usage = response.usage

        self.usages.append(response.usage)

        return response.choices[0].message.content


    def total_cost(self):

        return calc_total_price(self.usages)


# -------------------------------------------------------------------
# Parallel helper
# -------------------------------------------------------------------

def map_progress(pool, seq, f):

    results = []

    with tqdm(total=len(seq)) as progress:

        futures = []

        for el in seq:

            future = pool.submit(f, el)

            future.add_done_callback(lambda p: progress.update())

            futures.append(future)

        for future in futures:

            results.append(future.result())

    return results