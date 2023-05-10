import ast
import traceback
from colorama import Fore, Back, Style
from typing import Optional


class Node:
    """
    A class to represent a node in an abstract syntax tree (AST).

    Attributes:
        code (str): The code associated with the node.
        children (list): The child nodes of this node.
        start (int): The start index of the code in the original source.
        end (int): The end index of the code in the original source.
        intervals (list): List of intervals representing the code.
        tokens (list): List of tokens in the code.
        logprobs (list): List of log probabilities for the tokens.
        nll (float): Negative log likelihood of the code.
        deleted (bool): Whether the node is deleted.
        colon_name (str): The name of the colon in the code.
    """

    def __init__(self, code):
        self.code = code
        self.children = []
        self.start = 0
        self.end = 0
        self.intervals = []
        self.tokens = []
        self.logprobs = []
        self.nll = None
        self.deleted = None
        self.colon_name = None

    def __str__(self):
        def visit(n, pref):
            s = pref
            s += Fore.BLACK + Back.RED if n.deleted else Style.RESET_ALL
            s += f'"{n.code}"'
            s += str([self.code[t[0] : t[1]] for t in n.intervals])
            s += "[DELETED]" if n.deleted else ""
            s += Style.RESET_ALL
            s += "\n"
            for c in n.children:
                s += visit(c, pref + "\t")
            return s

        s = visit(self, "")
        return s

    def toJSON(self):
        return {
            "code": self.code,
            "start": self.start,
            "end": self.end,
            "intervals": self.intervals,
            "tokens": self.tokens,
            "logprobs": self.logprobs,
            "nll": self.nll,
            "deleted": self.deleted,
            "children": [c.toJSON() for c in self.children],
        }


def total_nodes(node: Node) -> int:
    """
    Calculates the total number of nodes in the abstract syntax tree (AST) rooted at the given node.

    Args:
        node (Node): The root node of the AST.

    Returns:
        int: The total number of nodes in the AST.
    """
    sum_c = 0
    for c in node.children:
        sum_c += total_nodes(c)
    return 1 + sum_c


class CheckVisitor(ast.NodeVisitor):
    """
    A class to visit nodes in an abstract syntax tree (AST).

    Attributes:
        code (str): The code to check.
        check (bool): Whether the code passes the check.
        print_flag (bool): Whether to print the check result.
    """

    def __init__(self, code, print_flag=False):
        self.code = code
        self.check = True
        self.print_flag = print_flag

    def visit(self, node: ast.AST) -> Optional[Node]:
        """
        Visits a node in the abstract syntax tree (AST) and returns a new Node object.

        This method visits a node in the AST, creates a new Node object with the code from the visited node,
        and recursively visits all child nodes. If the visited node is empty, it returns None.

        Args:
            node (ast.AST): The AST node to visit.

        Returns:
            Node: A new Node object with the code from the visited node and its children, or None if the visited node is empty.
        """
        if len(str(ast.unparse(node)).strip()) == 0:
            return None
        curr = Node(str(ast.unparse(node)))
        children = []
        for n in ast.iter_child_nodes(node):
            c_node = self.visit(n)
            if c_node is not None:
                children.append(c_node)
        curr.children = children
        return curr


def get_node(code: str, print_traceback: bool = False) -> Optional[Node]:
    """
    Parses the given code into an abstract syntax tree (AST) and returns the root node.

    Args:
        code (str): The code to parse.
        print_traceback (bool, optional): Whether to print the traceback if parsing fails. Defaults to False.

    Returns:
        Node: The root node of the AST, or None if parsing fails.
    """
    v = CheckVisitor(code)
    try:
        t = ast.parse(code)
    except:
        if print_traceback:
            print(traceback.format_exc())
        return None
    return v.visit(t)


def get_num_nodes_from_code(code: str) -> int:
    """
    Calculates the number of nodes in the abstract syntax tree (AST) for the given code.

    Args:
        code (str): The code to parse.

    Returns:
        int: The number of nodes in the AST, or -1 if parsing fails.
    """
    v = CheckVisitor(code)
    try:
        t = ast.parse(code)
    except:
        return -1
    n = v.visit(t)
    return total_nodes(n)


def check_code(code: str) -> bool:
    """
    Checks the given code by parsing it into an abstract syntax tree (AST) and visiting each node.

    Args:
        code (str): The code to check.

    Returns:
        bool: Whether the code passes the check.
    """
    v = CheckVisitor(code)
    t = ast.parse(code)
    n = v.visit(t)
    print(n)
    return v.check


if __name__ == "__main__":
    code = "x+1"
    print(get_num_nodes_from_code(code))
    print(check_code(code))
