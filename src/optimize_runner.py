import os
import sys
import numpy as np
from typing import List
import traceback
import ipdb
import argparse

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

import parse_results
from utils import utils
import optimize

PATH_TO_OUTPUT = "/home/akhakhar/shared/code-davinci"


def retrieve_results(output, fn, directories: List[str], path=PATH_TO_OUTPUT):
    for directory in directories:
        for file in [f for f in os.listdir(f"{PATH_TO_OUTPUT}/{directory}")]:
            fn(f"{PATH_TO_OUTPUT}/{directory}/{file}", output)
    return output


def is_subtree(a, b):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_name", dest="save_name", type=str, default="")
    parser.add_argument("--m", dest="m", type=int, default=1)
    parser.add_argument("--dataind", dest="dataind", type=int, default=-1)
    args = parser.parse_args()
    results = retrieve_results(
        [],
        lambda x, output: output.append(utils.read_json(x)),
        ["1672524017", "1672525916"],
    )

    max_costs = [-np.log(x) for x in [0.01, 0.5, 0.99]]
    output_data = []
    cnt_valid = 0

    results = [results[args.dataind]] if args.dataind >= 0 else results
    for i, sample in enumerate(results):
        print(f"[{i}/{len(results)}]{'-'*10}", flush=True)
        pred_str = "return" + sample["response"]["choices"][0]["text"].split("\n")[0]
        target_str = sample["prompt"]["solution"].strip()
        try:
            pred_tree = parse_results.code_to_final_ast(pred_str)
            parse_results.add_probability_to_nodes(
                pred_tree, sample["response"]["choices"][0]
            )
            target_tree = parse_results.code_to_final_ast(target_str)
        except:
            continue
        pruned_tree_data = optimize.create_tree_from_optimization_result_lst(
            pred_tree, args.m, max_costs
        )
        for j, optimize_output in enumerate(pruned_tree_data):
            print(f"\t[{j}/{len(pruned_tree_data)}]")
            print("Pruned Tree")
            print(pred_str)
            print(optimize_output["entire_tree_with_deleted"])
            print("Target")
            print(target_str)
            print(target_tree)
            print("-" * 10)
        cnt_valid += 1

    print(cnt_valid)
    utils.write_json("optimize_output.json", {"output": output_data})
