import ast
import traceback
from colorama import Fore, Back, Style


class Node:
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
            print(
                pref,
                # f"code:|{n.code}|",
                # f"[{n.start}-{n.end}]",
                # n.intervals,
                # "|",
                Fore.BLACK + Back.RED if n.deleted else Style.RESET_ALL,
                f'"{n.code}"',
                [self.code[t[0] : t[1]] for t in n.intervals],
                # n.tokens,
                "[DELETED]" if n.deleted else "",
                Style.RESET_ALL,
            )
            for c in n.children:
                visit(c, pref + "\t")

        visit(self, "")
        return ""


def total_nodes(node):
    sum_c = 0
    for c in node.children:
        sum_c += total_nodes(c)
    return 1 + sum_c


class CheckVisitor(ast.NodeVisitor):
    def __init__(self, code, print_flag=False):
        self.code = code
        self.check = True
        self.print_flag = print_flag

    def visit(self, node):
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


def get_node(code: str, print_traceback=False) -> Node:
    v = CheckVisitor(code)
    try:
        t = ast.parse(code)
    except:
        if print_traceback:
            print(traceback.format_exc())
        return None
    return v.visit(t)


def get_num_nodes_from_code(code):
    v = CheckVisitor(code)
    try:
        t = ast.parse(code)
    except:
        return -1
    n = v.visit(t)
    return total_nodes(n)


def check_code(code):
    v = CheckVisitor(code)
    t = ast.parse(code)
    n = v.visit(t)
    print(n)
    return v.check


if __name__ == "__main__":
    code = "x+1"
    print(get_num_nodes_from_code(code))
    print(check_code(code))
