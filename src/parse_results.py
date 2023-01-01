import os
import sys
from typing import List

PATH_TO_OUTPUT = "/home/akhakhar/shared/code-davinci"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

import ast_helper
from utils import utils


def execute_function_on_output(fn, directories: List[str], path=PATH_TO_OUTPUT):
    for directory in directories:
        for file in [f for f in os.listdir(f"{PATH_TO_OUTPUT}/{directories}")]:
            fn(utils.read_json(file))


def populate_start_and_end(parent):
    curr_ind = 0
    # assumes parent.children are in order of presence
    for child in parent.children:
        index_in_truncated_parent = parent.code[curr_ind:].index(child.code)
        child.start = parent.start + curr_ind + index_in_truncated_parent
        child.end = child.start + len(child.code)
        curr_ind = index_in_truncated_parent
    for child in parent.children:
        populate_start_and_end(child)


def assert_start_end_are_correct(parent, addtl):
    assert addtl[parent.start : parent.end] == parent.code
    for c in parent.children:
        assert_start_end_are_correct(c, addtl)


def make_dependent(parent):
    # window start
    prev_end = parent.start
    for i in range(len(parent.children)):
        if parent.children[i].start - prev_end > 0:
            parent.indices.append((prev_end, parent.children[i].start))
        prev_end = parent.children[i].end
    # last window end
    if len(parent.indices) > 0 and parent.children[-1].end < parent.end:
        parent.indices.append((parent.children[-1].end, parent.end))
    # case where no children
    if len(parent.children) == 0:
        parent.indices.append((parent.start, parent.end))
    for c in parent.children:
        make_dependent(c)


def code_to_final_ast(code: str):
    root = ast_helper.get_node(code)
    populate_start_and_end(root)
    root.end = len(root.code)
    assert_start_end_are_correct(root, root.code)
    make_dependent(root)
    print(root)


if __name__ == "__main__":
    data = utils.read_json(PATH_TO_OUTPUT + "/" + "1672524017/7")
    for key in data:
        print(key)
        print(data[key])
        print("---")
    code_to_final_ast(data["prompt"]["solution"].strip())
