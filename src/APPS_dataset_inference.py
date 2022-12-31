import os
import sys
import numpy as np
import ipdb


PATH_TO_DATA = "/home/akhakhar/data/APPS/test/"
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

from ast_helper import get_num_nodes_from_code

from utils import utils


def fetch_data_from_index(i: int):
    zero_padded = "0" * (4 - len(str(i))) + str(i)
    question = utils.read_file(PATH_TO_DATA + "/" + zero_padded + "/question.txt")
    solutions = utils.read_json(PATH_TO_DATA + "/" + zero_padded + "/solutions.json")
    return {"question": question, "solutions": solutions}


def prepare_inference_prompt_solution(
    question: str,
    solution: str,
    n=lambda x: x - 1,
    min_ast_num_nodes=7,
    pref="# Python\n# Complete the next line of the given code\n",
    post="\n# Solution:\n",
):
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
