import os
import sys
import numpy as np
import ipdb

PATH_TO_DATA = "/home/akhakhar/data/human_eval/HumanEval.jsonl"
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

from ast_helper import get_num_nodes_from_code
from utils import utils

data = utils.read_jsonl(PATH_TO_DATA)


def prepare_inference_prompt_solution(
    question: str,
    solution: str,
    n=lambda x: x - 1,
    min_ast_num_nodes=5,
    pref="# Python\n# Complete the next line of the given code\n",
    post="",
):
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
