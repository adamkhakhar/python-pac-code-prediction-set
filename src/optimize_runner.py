import os
import sys
import numpy as np
from typing import List

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)

import ast_helper
from utils import utils

PATH_TO_OUTPUT = "/home/akhakhar/shared/code-davinci"


def retrieve_results(fn, directories: List[str], path=PATH_TO_OUTPUT):
    for directory in directories:
        for file in [f for f in os.listdir(f"{PATH_TO_OUTPUT}/{directories}")]:
            fn(file)
