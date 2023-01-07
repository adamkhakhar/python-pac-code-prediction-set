from collections import deque
import os
import sys
import heapq
from typing import List

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)
import ast_helper


def duplicate_tree(node):
    curr_node = ast_helper.Node(node.code)
    curr_node.start = node.start
    curr_node.end = node.end
    curr_node.intervals = node.intervals
    curr_node.tokens = node.tokens
    curr_node.logprobs = node.logprobs
    curr_node.nll = node.nll
    curr_node.deleted = node.deleted
    curr_node.colon_name = node.colon_name

    for child in node.children:
        curr_node.children.append(duplicate_tree(child))
    return curr_node


def rm_deleted_nodes(node):
    if node is None or node.deleted:
        return None
    non_removed_children = []
    for child in node.children:
        rm_node = rm_deleted_nodes(child)
        if rm_node is not None:
            non_removed_children.append(rm_node)
    node.children = non_removed_children
    return node


def calculate_m(node):
    if node.deleted:
        return 1
    else:
        return sum([calculate_m(child) for child in node.children])


def greedy_removal(root, max_cost: float, m: int):
    map_node_to_parent = {}
    map_node_to_included_children = {}
    max_heap_cost_leaves = []
    q = deque()
    q.append(root)
    total_nodes = 0
    error_of_tree = 0
    # creates map_node_to_parents, max_heap_cost_leaves, total_nodes, error_of_tree
    while len(q) > 0:
        curr = q.popleft()
        total_nodes += 1
        error_of_tree += curr.nll
        map_node_to_included_children[curr] = len(curr.children)
        for child in curr.children:
            map_node_to_parent[child] = curr
            q.append(child)
        if len(curr.children) == 0:
            heapq.heappush(max_heap_cost_leaves, (-1 * curr.nll, curr))

    included_nodes = total_nodes
    while len(max_heap_cost_leaves) > 0 and error_of_tree > max_cost:
        # make sure removed node does not violate m
        curr_tree_m = calculate_m(root)
        cost, rm_node = None, None
        if curr_tree_m == m:
            # try removing each highest cost node nodes
            popped_nodes_to_be_added_bank = []
            rm_node_is_valid = False
            while not rm_node_is_valid:
                cost, rm_node = heapq.heappop(max_heap_cost_leaves)
                if len(rm_node.children) > 0 and all(
                    [n.deleted for n in rm_node.children]
                ):  # check to see if will increase m
                    rm_node_is_valid = True
                else:
                    popped_nodes_to_be_added_bank.append(rm_node)

            for node in popped_nodes_to_be_added_bank:
                heapq.heappush(max_heap_cost_leaves, (-1 * node.nll, node))
        else:
            cost, rm_node = heapq.heappop(max_heap_cost_leaves)
        rm_node.deleted = True
        total_nodes -= 1
        error_of_tree -= cost
        parent = map_node_to_parent[rm_node]
        map_node_to_included_children[parent] -= 1
        # add parent to tree if valid
        if map_node_to_included_children[parent] == 0:
            heapq.heappush(max_heap_cost_leaves, (-1 * parent.nll, parent))

    return {
        "pruned_root": rm_deleted_nodes(duplicate_tree(root)),
        "entire_tree_with_deleted": root,
        "check": "sat" if error_of_tree <= max_cost else "unsat",
        "error_of_tree": error_of_tree,
        "frac_included": included_nodes / total_nodes,
    }


def create_tree_from_optimization_result_lst(tree, m, max_cost_threshold: List):
    pruned_tree_data = []
    for max_cost in max_cost_threshold:
        copy_tree = duplicate_tree(tree)
        pruned_tree_data.append(greedy_removal(copy_tree), max_cost, m)
    return pruned_tree_data
