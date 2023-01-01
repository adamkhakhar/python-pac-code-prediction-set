import os
import sys
import numpy as np
import time

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(BASE_DIR)
LOG_PATH = "/home/akhakhar/shared/code-davinci/"
sys.path.append(BASE_DIR)
sys.path.append(ROOT_DIR)

from utils import utils
import APPS_dataset_inference
import humaneval_dataset_interface
import codex_interface

SLEEP_PER_REQ = 60


def execute_inference_humaneval(i: int, logging_dir: str, max_tokens=30):
    sample = humaneval_dataset_interface.data[i]
    prompt_dict = humaneval_dataset_interface.prepare_inference_prompt_solution(
        sample["prompt"],
        sample["canonical_solution"],
    )
    if prompt_dict is None:
        return None
    response = codex_interface.get_evaluation(
        prompt_dict["prompt"], max_tokens=max_tokens
    )
    data = {
        "prompt": prompt_dict,
        "response": dict(response),
        "name": logging_dir + str(i),
    }
    utils.write_json(data["name"], data)
    return data


if __name__ == "__main__":
    str_time_id = str(int(time.time()))
    logging_dir = LOG_PATH + str_time_id + "/"
    os.makedirs(logging_dir, exist_ok=True)
    cnt = 0
    for i in range(55, len(humaneval_dataset_interface.data)):
        data = execute_inference_humaneval(i, logging_dir)
        if data is None:
            print("data is none, skipping...")
            continue
        print("i:", i)
        print("solution:", data["prompt"]["solution"])
        pred_line = data["response"]["choices"][0]["text"].split("\n")[0].strip()
        print("prediction:", pred_line)
        print(
            "-" * 10 + "eql:",
            data["prompt"]["solution"].strip() == "return" + pred_line,
        )
        cnt += 1
        time.sleep(SLEEP_PER_REQ)
    print(logging_dir, cnt)
