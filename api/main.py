import asyncio
from openai import OpenAI
from pydantic import BaseModel
import dotenv
from serpapi import GoogleSearch
import os

dotenv.load_dotenv()


def openai_test():
    client = OpenAI()

    class Step(BaseModel):
        explanation: str
        output: str

    class MathReasoning(BaseModel):
        steps: list[Step]
        final_answer: float

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input="how can I solve 8x + 7 = -23",
        text_format=MathReasoning,
    )

    math_reasoning: MathReasoning | None = response.output_parsed
    if math_reasoning is not None:
        print(math_reasoning.final_answer)


def serpapi_test():
    params = {
        "engine": "google",
        "q": "Coffee",
        "location": "Austin, Texas, United States",
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "api_key": os.environ["SERP_API_KEY"],
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print(results)


async def main():
    serpapi_test()


if __name__ == "__main__":
    asyncio.run(main())

"""
steps=[
Step(explanation='Start with the original equation.', output='8x + 7 = -23'), 
Step(explanation='Subtract 7 from both sides to isolate the term with the variable on one side. This simplifies the equation.', output='8x = -23 - 7'), 
Step(explanation='Calculate -23 - 7.', output='8x = -30'), 
Step(explanation='Divide both sides by 8 to solve for x.', output='x = -30 / 8'), 
Step(explanation='Simplify -30 / 8 to its simplest form.', output='x = -15/4')
] 

final_answer='x = -\\frac{15}{4}'
"""
