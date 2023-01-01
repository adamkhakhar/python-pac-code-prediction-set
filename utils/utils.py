import os
import json
from typing import List


def read_file(path):
    with open(path) as f:
        return str(f.read())


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path: str, d: dict):
    with open(path, "w") as f:
        json.dump(d, f)


def read_jsonl(path):
    l = []
    with open(path) as f:
        json_list = list(f)
    for json_str in json_list:
        result = json.loads(json_str)
        l.append(result)
    return l


def comment_out_lines(s, start=-1, end=-1):
    split_s = s.split("\n")
    if start == -1:
        start = 0
    if end == -1:
        end = len(split_s)
    for i in range(len(split_s)):
        if i >= start and i <= end:
            if not split_s[i].startswith("#"):
                split_s[i] = "# " + split_s[i]
    return "\n".join(split_s)


def replace_all_print_with_return(l: List[str]) -> List[str]:
    # assumes if print exists in line, the last character is the ending paranthesis of the print function
    for i in range(len(l)):
        if "print(" in l[i]:
            l[i] = l[i].rstrip()[:-1]  # rm ending paranthesis
            l[i] = l[i].replace("print(", "return ")
    return l
