import os
import openai
import sys
import pprint

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)

from utils.utils import read_file

PATH_TO_OPEN_AI_KEY = "/home/akhakhar/keys/OPEN_AI_API_KEY"
openai.api_key = read_file(PATH_TO_OPEN_AI_KEY).strip("\n")


def get_evaluation(
    prompt: str,
    logprobs: int = 1,
    max_tokens: int = 50,
    model: str = "code-davinci-002",
) -> openai.openai_object.OpenAIObject:
    """
    Generate a completion for a given prompt using the specified OpenAI model.

    This function uses the OpenAI API to generate a completion for a given prompt.
    It allows for customization of the model used, the number of log probabilities to return,
    and the maximum number of tokens in the generated completion.

    Args:
        prompt (str): The prompt to generate a completion for.
        logprobs (int, optional): The number of most probable tokens to return for each position. Defaults to 1.
        max_tokens (int, optional): The maximum number of tokens in the generated completion. Defaults to 50.
        model (str, optional): The model to use for generating the completion. Defaults to "code-davinci-002".

    Returns:
        openai.openai_object.OpenAIObject: The generated completion.
    """
    return openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=logprobs,
        max_tokens=max_tokens,
    )


if __name__ == "__main__":
    prompt = """
    # Python3. Only respond with the code to complete the line.
    # return sum of list l of floats
    from typing import List
    def sum(l : List[int]) -> int:
        return"""
    res = get_evaluation(prompt, model="davinci", logprobs=2)
    pprint.pprint(res)
