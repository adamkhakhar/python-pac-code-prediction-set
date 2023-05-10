from collections import deque
import os
import sys
import heapq
from typing import List, Optional, Dict, Union
import code
import traceback

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)
import ast_helper


def duplicate_tree(node: ast_helper.Node) -> ast_helper.Node:
    """
    Creates a deep copy of the given node and its subtree.

    Args:
        node (ast_helper.Node): The root node of the subtree to duplicate.

    Returns:
        ast_helper.Node: A deep copy of the given node and its subtree.
    """
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


def rm_deleted_nodes(node: ast_helper.Node) -> Optional[ast_helper.Node]:
    """
    Removes deleted nodes from the given node's subtree.

    Args:
        node (Node): The root node of the subtree to remove deleted nodes from.

    Returns:
        Node: The root node of the subtree with deleted nodes removed, or None if the given node is deleted.
    """
    if node is None or node.deleted:
        return None
    non_removed_children = []
    for child in node.children:
        rm_node = rm_deleted_nodes(child)
        if rm_node is not None:
            non_removed_children.append(rm_node)
    node.children = non_removed_children
    return node


def calculate_m(node: ast_helper.Node) -> int:
    """
    Calculates the number of deleted holes in the given node's subtree.

    Args:
        node (Node): The root node of the subtree to calculate the number of deleted nodes in.

    Returns:
        int: The number of deleted nodes in the given node's subtree.
    """
    if node.deleted:
        return 1
    else:
        return sum([calculate_m(child) for child in node.children])


def map_node_to_subtree_cost(root: ast_helper.Node) -> Dict[ast_helper.Node, float]:
    """
    Maps each node in the given node's subtree to its subtree cost.

    Args:
        root (Node): The root node of the subtree to map nodes to subtree costs in.

    Returns:
        dict: A dictionary mapping each node in the given node's subtree to its subtree cost.
    """
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


def del_node_and_all_children(node: ast_helper.Node) -> None:
    """
    Marks the given node and all its descendants as deleted.

    Args:
        node (Node): The root node of the subtree to mark as deleted.
    """
    node.deleted = True
    for c in node.children:
        del_node_and_all_children(c)


def num_node_not_deleted(node: ast_helper.Node) -> int:
    """
    Calculates the number of undeleted nodes in the given node's subtree.

    Args:
        node (Node): The root node of the subtree to calculate the number of undeleted nodes in.

    Returns:
        int: The number of undeleted nodes in the given node's subtree.
    """
    if node.deleted:
        return 0
    else:
        return 1 + sum([num_node_not_deleted(child) for child in node.children])


def calculate_error_of_tree_undeleted(node: ast_helper.Node) -> float:
    """
    Calculates the total error of the undeleted nodes in the given node's subtree.

    Args:
        node (Node): The root node of the subtree to calculate the total error of undeleted nodes in.

    Returns:
        float: The total error of the undeleted nodes in the given node's subtree.
    """
    if node.deleted:
        return 0
    else:
        return node.nll + sum(
            [calculate_error_of_tree_undeleted(child) for child in node.children]
        )


def greedy_removal(
    root: ast_helper.Node, max_cost: float, m: int
) -> Dict[str, Union[ast_helper.Node, str, float, float]]:
    """
    Prunes the given node's subtree using a greedy algorithm to minimize the total error while keeping the total cost below a maximum threshold.

    Args:
        root (Node): The root node of the subtree to prune.
        max_cost (float): The maximum total cost threshold.
        m (int): The minimum number of nodes to keep in the subtree.

    Returns:
        dict: A dictionary containing the pruned root, the entire tree with deleted nodes, a check status, the total error of the tree, and the fraction of nodes included.
    """
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


def create_tree_from_optimization_result_lst(
    tree: ast_helper.Node, m: int, max_cost_threshold: List[float]
) -> List[Dict[str, Union[ast_helper.Node, str, float, float]]]:
    """
    Creates a list of pruned trees from the given tree for each maximum cost threshold in the given list.

    Args:
        tree (Node): The root node of the tree to prune.
        m (int): The minimum number of nodes to keep in the tree.
        max_cost_threshold (List[float]): A list of maximum total cost thresholds.

    Returns:
        list: A list of dictionaries, each containing a pruned tree for a maximum cost threshold in the given list.
    """
    pruned_tree_data = []
    for max_cost in max_cost_threshold:
        copy_tree = duplicate_tree(tree)
        pruned_tree_data.append(greedy_removal(copy_tree, max_cost, m))
    return pruned_tree_data
