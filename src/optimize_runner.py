import os
import sys
import numpy as np
from typing import List
import traceback
import ipdb

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

import parse_results
from utils import utils

PATH_TO_OUTPUT = "/home/akhakhar/shared/code-davinci"


def retrieve_results(output, fn, directories: List[str], path=PATH_TO_OUTPUT):
    for directory in directories:
        for file in [f for f in os.listdir(f"{PATH_TO_OUTPUT}/{directory}")]:
            fn(f"{PATH_TO_OUTPUT}/{directory}/{file}", output)
    return output


def is_subtree(a, b):
    pass


if __name__ == "__main__":
    results = retrieve_results(
        [],
        lambda x, output: output.append(utils.read_json(x)),
        ["1672524017", "1672525916"],
    )
    cnt_valid = 0
    for i, sample in enumerate(results):
        print(f"[{i}/{len(results)}]{'-'*10}", flush=True)
        pred_str = "return" + sample["response"]["choices"][0]["text"].split("\n")[0]
        target_str = sample["prompt"]["solution"].strip()
        print(pred_str)
        print(target_str)
        try:
            pred_tree = parse_results.code_to_final_ast(pred_str)
            parse_results.add_probability_to_nodes(
                pred_tree, sample["response"]["choices"][0]
            )
            target_tree = parse_results.code_to_final_ast(target_str)
        except:
            continue
        cnt_valid += 1

    print(cnt_valid)
