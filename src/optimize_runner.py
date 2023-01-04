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


def is_subtree(target_root_code, target, pruned_root_code, pruned):
    # check if pruned tree is subtree of target tree
    def get_string_intervals(code, n):
        return "#".join([code[t[0] : t[1]] for t in n.intervals])

    if pruned is None:
        return {"eval": True, "reason": "Pruned is None"}
    curr_node_same = get_string_intervals(
        target_root_code, target
    ) == get_string_intervals(pruned_root_code, pruned)
    if curr_node_same:

        def map_string_interval_to_ind(root_code, children):
            map_interval_to_ind = {}
            for i in range(len(children)):
                if not children[i].deleted:
                    map_interval_to_ind[
                        get_string_intervals(root_code, children[i])
                    ] = i
            return map_interval_to_ind

        target_children_map_interval_to_ind = map_string_interval_to_ind(
            target_root_code, target.children
        )
        pruned_children_map_interval_to_ind = map_string_interval_to_ind(
            pruned_root_code, pruned.children
        )
        # check if all pruned children are in target children
        for pruned_child_str in pruned_children_map_interval_to_ind:
            if pruned_child_str not in target_children_map_interval_to_ind:
                return {
                    "eval": False,
                    "reason": f"Pred child ({pruned_child_str}) not in target_children_set ({target_children_map_interval_to_ind.keys()})",
                }
        # check if pruned child node is subtree of relevant target children node
        for target_child_str in target_children_map_interval_to_ind:
            if target_child_str in pruned_children_map_interval_to_ind:
                eval = is_subtree(
                    target_root_code,
                    target.children[
                        target_children_map_interval_to_ind[target_child_str]
                    ],
                    pruned_root_code,
                    pruned.children[
                        pruned_children_map_interval_to_ind[target_child_str]
                    ],
                )
                if not eval["eval"]:
                    return eval
        return {"eval": True}
    else:
        return {
            "eval": False,
            "reason": "Curr nodes are not the same: "
            + str([target_root_code[t[0] : t[1]] for t in target.intervals])
            + " vs "
            + str([pruned_root_code[t[0] : t[1]] for t in pruned.intervals]),
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", dest="m", type=int, default=1)
    parser.add_argument("--dataind", dest="dataind", type=int, default=-1)
    parser.add_argument("--noprint", action="store_false")
    args = parser.parse_args()
    results = retrieve_results(
        [],
        lambda x, output: output.append(utils.read_json(x)),
        ["1672524017", "1672525916"],
    )

    max_costs = [-np.log(x) for x in np.linspace(1e-5, 1 - 1e-5, 100)]

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
            save_data = {}
            try:
                if args.noprint:
                    print(f"\t[{j}/{len(pruned_tree_data)}]")
                    print("Pruned Tree")
                    print(pred_str)
                    print(optimize_output["entire_tree_with_deleted"])
                    print("Target")
                    print(target_str)
                    print(target_tree)
                    print("-" * 10)
                    print(
                        is_subtree(
                            target_tree.code,
                            target_tree,
                            pred_tree.code,
                            optimize_output["entire_tree_with_deleted"],
                        )
                    )
                save_data["pred_in_target"] = is_subtree(
                    target_tree.code,
                    target_tree,
                    pred_tree.code,
                    optimize_output["entire_tree_with_deleted"],
                )
                save_data["pred_str"] = pred_str
                save_data["target_str"] = target_str
                save_data["cost"] = max_costs[j]
                save_data["data_ind"] = i
                save_data["tau_ind"] = j
                save_data["output"] = optimize_output
                save_data["output"]["pruned_root"] = save_data["output"][
                    "pruned_root"
                ].toJSON()
                save_data["output"]["entire_tree_with_deleted"] = save_data["output"][
                    "entire_tree_with_deleted"
                ].toJSON()
                save_data["output"]["check"] = str(save_data["output"]["check"])
                output_data.append(save_data)
            except:
                traceback.print_exc()
                continue
        cnt_valid += 1

    print(cnt_valid)
    os.makedirs(f"{ROOT_DIR}/results", exist_ok=True)
    utils.write_json(
        f"{ROOT_DIR}/results/optimize_output_{args.dataind}.json",
        {"output": output_data},
    )
