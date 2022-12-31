import os
import openai
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)

from utils.utils import read_file

PATH_TO_OPEN_AI_KEY = "/home/akhakhar/keys/OPEN_AI_API_KEY"
openai.api_key = read_file(PATH_TO_OPEN_AI_KEY).strip("\n")


def get_evaluation(prompt: str, logprobs=1, max_tokens=50, model="code-davinci-002"):
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
    # Python
    # return sum of list l of floats
    from typing import List
    def sum(l : List[int]) -> int:
        return"""
    print(get_evaluation(prompt))
