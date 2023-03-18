from collections import deque
import os
import sys
import heapq
from typing import List
import code
import traceback

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


def map_node_to_subtree_cost(root):
    subtree_cost_map = {}

    def recursive_cost(node):
        if len(node.children) == 0:
            subtree_cost_map[node] = node.nll
        else:
            subtree_cost_map[node] = node.nll + sum(
                [recursive_cost(c) for c in node.children]
            )
        return subtree_cost_map[node]

    recursive_cost(root)
    return subtree_cost_map


def del_node_and_all_children(node):
    node.deleted = True
    for c in node.children:
        del_node_and_all_children(c)


def num_nodes_all(node):
    return (1 + sum([num_nodes(c) for c in node.children])) if node is not None else 0


def num_node_not_deleted(node):
    if node.deleted:
        return 0
    else:
        return 1 + sum([num_node_not_deleted(child) for child in node.children])


def calculate_error_of_tree_undeleted(node):
    if node.deleted:
        return 0
    else:
        return node.nll + sum(
            [calculate_error_of_tree_undeleted(child) for child in node.children]
        )


# def greedy_removal(root, max_cost: float, m: int):
#     assert m == 1
#     print("\nGREEDY_REMOVAL")
#     subtree_cost_map = map_node_to_subtree_cost(root)
#     subtree_cost_map[None] = 0
#     best_rm_node = None
#     for node in subtree_cost_map:
#         if subtree_cost_map[root] - subtree_cost_map[node] <= max_cost:
#             if (
#                 best_rm_node is None
#                 or subtree_cost_map[best_rm_node] > subtree_cost_map[node]
#             ):
#                 best_rm_node = node
#     if best_rm_node is not None:
#         del_node_and_all_children(best_rm_node)
#     error_of_tree = subtree_cost_map[root] - subtree_cost_map[best_rm_node]
#     total_nodes = num_nodes_all(root)
#     included_nodes = total_nodes - num_nodes_all(best_rm_node)
#     return {
#         "pruned_root": rm_deleted_nodes(duplicate_tree(root)),
#         "entire_tree_with_deleted": root,
#         "check": "sat" if error_of_tree <= max_cost else "unsat",
#         "error_of_tree": error_of_tree,
#         "frac_included": included_nodes / total_nodes,
#     }


def greedy_removal(root, max_cost: float, m: int):
    assert m > 0
    print("\nGREEDY_REMOVAL")
    subtree_cost_map = map_node_to_subtree_cost(root)
    subtree_cost_map[None] = 0
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

    max_heap_cost_leaves_parent_of_rm_nodes = []
    print("error_of_tree", error_of_tree)
    print("max_cost", max_cost)
    while len(max_heap_cost_leaves) > 0 and error_of_tree > max_cost:
        # make sure removed node does not violate m
        curr_tree_m = calculate_m(root)
        print("---")
        print("\tcurr_m", curr_tree_m)
        print("\terror_of_tree", error_of_tree)
        print(
            "\tCURR MAX HEAP",
            [(c, n.get_interval_str(root.code, n)) for c, n in max_heap_cost_leaves],
        )
        rm_node = None
        if curr_tree_m == m:
            # remove largest cost node of parent of nodes already removed
            _, rm_node = heapq.heappop(max_heap_cost_leaves_parent_of_rm_nodes)
        else:
            # rm the largest leaf node
            cost, rm_node = heapq.heappop(max_heap_cost_leaves)
        print("\tRemoved Node", rm_node.get_interval_str(root.code, rm_node))
        del_node_and_all_children(rm_node)
        error_of_tree = calculate_error_of_tree_undeleted(root)
        parent = map_node_to_parent[rm_node]
        map_node_to_included_children[parent] -= 1
        # add parent to tree if valid
        if map_node_to_included_children[parent] == 0:
            try:
                heapq.heappush(max_heap_cost_leaves, (-1 * parent.nll, parent))
            except:
                traceback.print_exc()
                code.interact(local=locals())
        # update the max_heap_cost_leaves_parent_of_rm_nodes
        heapq.heappush(
            max_heap_cost_leaves_parent_of_rm_nodes, (-1 * parent.nll, parent)
        )

    error_of_tree = calculate_error_of_tree_undeleted(root)
    return {
        "pruned_root": rm_deleted_nodes(duplicate_tree(root)),
        "entire_tree_with_deleted": root,
        "check": "sat" if error_of_tree <= max_cost else "unsat",
        "error_of_tree": error_of_tree,
        "frac_included": num_node_not_deleted(root) / total_nodes,
    }


# def greedy_removal(root, max_cost: float, m: int):
#     print("\nGREEDY_REMOVAL")
#     map_node_to_parent = {}
#     map_node_to_included_children = {}
#     max_heap_cost_leaves = []
#     q = deque()
#     q.append(root)
#     total_nodes = 0
#     error_of_tree = 0
#     # creates map_node_to_parents, max_heap_cost_leaves, total_nodes, error_of_tree
#     while len(q) > 0:
#         curr = q.popleft()
#         total_nodes += 1
#         error_of_tree += curr.nll
#         map_node_to_included_children[curr] = len(curr.children)
#         for child in curr.children:
#             map_node_to_parent[child] = curr
#             q.append(child)
#         if len(curr.children) == 0:
#             heapq.heappush(max_heap_cost_leaves, (-1 * curr.nll, curr))

#     included_nodes = total_nodes
#     print("included_nodes", included_nodes)
#     print("error_of_tree", error_of_tree)
#     print("max_cost", max_cost)
#     while len(max_heap_cost_leaves) > 0 and error_of_tree > max_cost:
#         # make sure removed node does not violate m
#         curr_tree_m = calculate_m(root)
#         print("---")
#         print("\tcurr_m", curr_tree_m)
#         print("\terror_of_tree", error_of_tree)
#         print("\tCURR MAX HEAP", [(c, n.get_interval_str(root.code, n)) for c, n in max_heap_cost_leaves])
#         cost, rm_node = None, None
#         if curr_tree_m == m:
#             # try removing each highest cost node nodes
#             popped_nodes_to_be_added_bank = []
#             rm_node_is_valid = False
#             while not rm_node_is_valid:
#                 cost, rm_node = heapq.heappop(max_heap_cost_leaves)
#                 if len(rm_node.children) > 0 and all(
#                     [n.deleted for n in rm_node.children]
#                 ):  # check to see if will increase m
#                     rm_node_is_valid = True
#                 else:
#                     popped_nodes_to_be_added_bank.append(rm_node)

#             for node in popped_nodes_to_be_added_bank:
#                 heapq.heappush(max_heap_cost_leaves, (-1 * node.nll, node))
#         else:
#             cost, rm_node = heapq.heappop(max_heap_cost_leaves)
#         print("\tRemoved Node", rm_node.get_interval_str(root.code, rm_node))
#         rm_node.deleted = True
#         total_nodes -= 1
#         error_of_tree -= rm_node.nll
#         parent = map_node_to_parent[rm_node]
#         map_node_to_included_children[parent] -= 1
#         # add parent to tree if valid
#         if map_node_to_included_children[parent] == 0:
#             heapq.heappush(max_heap_cost_leaves, (-1 * parent.nll, parent))

#     return {
#         "pruned_root": rm_deleted_nodes(duplicate_tree(root)),
#         "entire_tree_with_deleted": root,
#         "check": "sat" if error_of_tree <= max_cost else "unsat",
#         "error_of_tree": error_of_tree,
#         "frac_included": included_nodes / total_nodes,
#     }


def create_tree_from_optimization_result_lst(tree, m, max_cost_threshold: List):
    pruned_tree_data = []
    for max_cost in max_cost_threshold:
        copy_tree = duplicate_tree(tree)
        pruned_tree_data.append(greedy_removal(copy_tree, max_cost, m))
    return pruned_tree_data
