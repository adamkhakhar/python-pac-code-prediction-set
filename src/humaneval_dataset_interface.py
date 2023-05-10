import os
import sys
import numpy as np
from typing import Optional, Dict, Union

PATH_TO_DATA = "/home/akhakhar/data/human_eval/HumanEval.jsonl"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

from ast_helper import get_num_nodes_from_code
from utils import utils

data = utils.read_jsonl(PATH_TO_DATA)


def prepare_inference_prompt_solution(
    question: str,
    solution: str,
    n: Callable[[int], int] = lambda x: x - 1,
    min_ast_num_nodes: int = 5,
    pref: str = "# Python\n# Complete the next line of the given code\n",
    post: str = "",
) -> Optional[Dict[str, Union[str, int]]]:
    """
    Prepares an inference prompt and solution from a given question and solution.

    This function prepares an inference prompt and solution from a given question and solution. It ensures that the
    next line of code is complex enough (based on the number of nodes in its abstract syntax tree) to be a good sample.
    If the next line is not complex enough, the function returns None.

    Args:
        question (str): The question to prepare the inference prompt from.
        solution (str): The solution to prepare the inference prompt from.
        n (Callable[[int], int], optional): A function to determine the number of lines shown. Defaults to lambda x: x - 1.
        min_ast_num_nodes (int, optional): The minimum number of AST nodes for the line to be considered complicated enough. Defaults to 5.
        pref (str, optional): The prefix to add to the prompt. Defaults to "# Python\n# Complete the next line of the given code\n".
        post (str, optional): The postfix to add to the prompt. Defaults to "".

    Returns:
        dict: A dictionary containing the prepared prompt, solution, number of lines shown, and the whole solution, or None if the next line is not complex enough.
    """
    solution_lst = [line for line in solution.split("\n") if len(line.strip()) > 0]
    solution_lst = utils.replace_all_print_with_return(solution_lst)
    lines_shown = n(len(solution_lst))
    next_line = solution_lst[lines_shown]
    # make sure the line is complicated enough to be a good sample
    if get_num_nodes_from_code(next_line.strip()) < min_ast_num_nodes:
        return None
    first_n = "\n".join(solution_lst[:lines_shown])
    # add final return substring
    first_n += "\n" + next_line[: next_line.index("return") + len("return")]
    return {
        "prompt": pref + question + post + first_n,
        "solution": next_line,
        "n": lines_shown,
        "whole_solution": solution,
    }


if __name__ == "__main__":
    cnt = 0
    for i in range(len(data)):
        res = prepare_inference_prompt_solution(
            data[0]["prompt"], data[i]["canonical_solution"]
        )
        if res is not None:
            cnt += 1
            for key in res:
                print("-" * 10, key, "-" * 10)
                print(res[key], end="")
    print(cnt)
