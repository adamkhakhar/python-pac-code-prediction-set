import os
import sys
import numpy as np
from typing import List, Dict, Union, Callable


PATH_TO_DATA = "/home/akhakhar/data/APPS/test/"
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

from ast_helper import get_num_nodes_from_code

from utils import utils


def fetch_data_from_index(i: int) -> Dict[str, Union[str, Dict]]:
    """
    Fetches question and solutions data from a specified index.

    Args:
        i (int): The index from which to fetch the data.

    Returns:
        dict: A dictionary containing the question and solutions data.
    """

    zero_padded = "0" * (4 - len(str(i))) + str(i)
    question = utils.read_file(PATH_TO_DATA + "/" + zero_padded + "/question.txt")
    solutions = utils.read_json(PATH_TO_DATA + "/" + zero_padded + "/solutions.json")
    return {"question": question, "solutions": solutions}


def prepare_inference_prompt_solution(
    question: str,
    solution: str,
    n: Callable[[int], int] = lambda x: x - 1,
    min_ast_num_nodes: int = 7,
    pref: str = "# Python\n# Complete the next line of the given code\n",
    post: str = "\n# Solution:\n",
) -> Dict[str, Union[str, int]]:
    """
    Prepares an inference prompt and solution from a given question and solution.

    Args:
        question (str): The question to prepare the inference prompt from.
        solution (str): The solution to prepare the inference prompt from.
        n (Callable[[int], int], optional): A function to determine the number of lines shown. Defaults to lambda x: x - 1.
        min_ast_num_nodes (int, optional): The minimum number of AST nodes for the line to be considered complicated enough. Defaults to 7.
        pref (str, optional): The prefix to add to the prompt. Defaults to "# Python\n# Complete the next line of the given code\n".
        post (str, optional): The postfix to add to the prompt. Defaults to "\n# Solution:\n".

    Returns:
        dict: A dictionary containing the prepared prompt, solution, number of lines shown, and the whole solution.
    """
    commented_question = utils.comment_out_lines(question)
    solution_lst = [line for line in solution.split("\n") if len(line.strip()) > 0]
    lines_shown = n(len(solution_lst))
    next_line = solution_lst[lines_shown].strip()
    # make sure the line is complicated enough to be a good sample
    while get_num_nodes_from_code(next_line) < min_ast_num_nodes and lines_shown > 0:
        lines_shown -= 1
        next_line = "\n".join(solution_lst[lines_shown:])
    first_n = "\n".join(solution_lst[:lines_shown])
    return {
        "prompt": pref + commented_question + post + first_n,
        "solution": next_line,
        "n": lines_shown,
        "whole_solution": solution,
    }


if __name__ == "__main__":
    for i in range(5):
        question_data = fetch_data_from_index(i)
        x = prepare_inference_prompt_solution(
            question_data["question"], question_data["solutions"][0]
        )
        for key in x:
            print("-" * 10, "key:", key, "-" * 10)
            print(x[key])
