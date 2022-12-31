import ast
import ipdb


class Node:
    def __init__(self, code):
        self.code = code
        self.children = []

    def __str__(self):
        def visit(n, pref):
            print(pref, n.code)
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
        curr = Node(str(ast.unparse(node)))
        children = []
        for n in ast.iter_child_nodes(node):
            children.append(self.visit(n))
        curr.children = children
        return curr


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
