from typing import Dict, Any

from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.chains.llm import LLMChain
from langchain.chains.sequential import SequentialChain
import os

model = OpenAI(model_name = "gpt-3.5-turbo-instruct",
               openai_api_key = os.environ.get("OPENAI_API_KEY"), )


def generateAnswer(country: str) -> dict[str, Any]:
    capital_template: PromptTemplate = PromptTemplate(template = "What is the capital of {country} name",
                                                      input_variables = ["country"])
    famous_template = PromptTemplate(template = "Tell me a famous name from {capital}", input_variables = ['capital'])

    capitalChain: LLMChain = LLMChain(llm = model, prompt = capital_template, output_key = "capital")
    famousChain: LLMChain = LLMChain(llm = model, prompt = famous_template)

    chain = SequentialChain(chains = [capitalChain, famousChain], input_variables = ["country"],
                            output_variables = ["country", "capital"])
    response = chain({'country': country})
    return response


if __name__ == "__main__":
    print(generateAnswer(country = "Romania"))
