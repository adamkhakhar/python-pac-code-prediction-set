import os
import sys
from typing import List
import numpy as np

PATH_TO_OUTPUT = "/home/akhakhar/shared/code-davinci"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)

import ast_helper
from utils import utils


def populate_start_and_end(parent: ast_helper.Node) -> None:
    """
    Populates the start and end attributes of each node in the AST.

    Args:
        parent (ast_helper.Node): The root of the AST.
    """
    curr_ind = 0
    # assumes parent.children are in order of presence
    for child in parent.children:
        index_in_truncated_parent = parent.code[curr_ind:].index(child.code)
        child.start = parent.start + curr_ind + index_in_truncated_parent
        child.end = child.start + len(child.code)
        curr_ind = index_in_truncated_parent + len(child.code)
    for child in parent.children:
        populate_start_and_end(child)


def assert_start_end_are_correct(parent: ast_helper.Node, addtl: str) -> None:
    """
    Asserts that the start and end attributes of each node in the AST are correct.

    Args:
        parent (ast_helper.Node): The root of the AST.
        addtl (str): The code string.
    """
    assert addtl[parent.start : parent.end] == parent.code
    for c in parent.children:
        assert_start_end_are_correct(c, addtl)


def make_dependent(parent: ast_helper.Node) -> None:
    """
    Populates the intervals attribute of each node in the AST.

    Args:
        parent (ast_helper.Node): The root of the AST.
    """
    # window start
    prev_end = parent.start
    for i in range(len(parent.children)):
        if parent.children[i].start - prev_end > 0:
            parent.intervals.append((prev_end, parent.children[i].start))
        prev_end = parent.children[i].end
    # last window end
    if len(parent.intervals) > 0 and parent.children[-1].end < parent.end:
        parent.intervals.append((parent.children[-1].end, parent.end))
    # case where no children
    if len(parent.children) == 0:
        parent.intervals.append((parent.start, parent.end))
    for c in parent.children:
        make_dependent(c)


def remove_all_spaces_in_code(parent: ast_helper.Node) -> ast_helper.Node:
    """
    Removes all spaces in the code attribute of each node in the AST.

    Args:
        parent (ast_helper.Node): The root of the AST.

    Returns:
        ast_helper.Node: The root of the AST with all spaces removed from the code.
    """
    parent.code = parent.code.replace(" ", "")
    for i in range(len(parent.children)):
        parent.children[i] = remove_all_spaces_in_code(parent.children[i])
    return parent


def code_to_final_ast(code: str) -> ast_helper.Node:
    """
    Converts code into an AST and populates the start, end, and intervals attributes of each node.

    Args:
        code (str): The code string.

    Returns:
        ast_helper.Node: The root of the AST.
    """
    root = ast_helper.get_node(code)
    remove_all_spaces_in_code(root)
    populate_start_and_end(root)
    root.end = len(root.code)
    assert_start_end_are_correct(root, root.code)
    make_dependent(root)
    return root


def intervals_to_token_probs(
    parent: ast_helper.Node,
    map_index_to_token_ind: dict,
    tokens: List[str],
    token_logprobs: List[float],
) -> None:
    """
    Populates the tokens, logprobs, and nll attributes of each node in the AST.

    Args:
        parent (ast_helper.Node): The root of the AST.
        map_index_to_token_ind (dict): A mapping from output index to token index.
        tokens (List[str]): The list of tokens.
        token_logprobs (List[float]): The list of log probabilities for each token.
    """
    token_inds = []
    for tup in parent.intervals:
        for output_index in range(tup[0], tup[1]):
            token_inds.append(map_index_to_token_ind[output_index])
    token_inds = set(token_inds)
    for token_ind in token_inds:
        parent.tokens.append(tokens[token_ind])
        parent.logprobs.append(token_logprobs[token_ind])
    parent.nll = -1 * sum(parent.logprobs)
    for c in parent.children:
        intervals_to_token_probs(c, map_index_to_token_ind, tokens, token_logprobs)


def add_probability_to_nodes(
    root: ast_helper.Node, response: dict, debug: bool = False
) -> None:
    """
    Adds probability information to each node in the AST.

    Args:
        root (ast_helper.Node): The root of the AST.
        response (dict): The response from the model.
        debug (bool, optional): Whether to print debug information. Defaults to False.
    """
    # remove all spaces in tokens
    response["logprobs"]["tokens"] = [
        tok.replace(" ", "") for tok in response["logprobs"]["tokens"]
    ]
    map_index_to_token_ind = {}
    output_index = 0
    for i in range(len(response["logprobs"]["tokens"])):
        for _ in range(len(response["logprobs"]["tokens"][i])):
            map_index_to_token_ind[output_index] = i
            output_index += 1
    if debug:
        for key in map_index_to_token_ind:
            print(
                key, "->", response["logprobs"]["tokens"][map_index_to_token_ind[key]]
            )
        print("----")
        for i in range(len(root.code)):
            print(i, "->", root.code[i])
        print("----")
    intervals_to_token_probs(
        root,
        map_index_to_token_ind,
        response["logprobs"]["tokens"],
        response["logprobs"]["token_logprobs"],
    )
