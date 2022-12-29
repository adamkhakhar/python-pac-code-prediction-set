import os
import openai
import sys
import ipdb

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)

from utils.utils import read_file

openai.api_key = read_file("/home/akhakhar/keys/OPEN_AI_API_KEY").strip("\n")


def get_evaluation(prompt: str, logprobs=1, model="code-davinci-002"):
    return openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        logprobs=logprobs,
    )
