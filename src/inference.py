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
import codex_interface


def execute_inference(i: int):
    sample = APPS_dataset_inference.fetch_data_from_index(i)
    prompt_dict = APPS_dataset_inference.prepare_inference_prompt_solution(
        sample["question"],
        sample["solutions"][np.random.randint(low=0, high=len(sample["solutions"]))],
    )
    response = codex_interface.get_evaluation(prompt_dict["prompt"])
    name = LOG_PATH + str(i) + "_" + str(int(time.time()))
    data = {
        "prompt": prompt_dict,
        "response": dict(response),
        "name": LOG_PATH + str(i) + "_" + str(int(time.time())),
    }
    utils.write_json(name, data)
    return data


if __name__ == "__main__":
    for i in range(5):
        data = execute_inference(i)
        print("name", data["name"])
        print("solution", data["prompt"]["solution"])
        pred_line = data["response"]["choices"][0]["text"].split()[0].strip()
        print("prediction", pred_line)
        print("-" * 10 + "eql:", data["prompt"]["solution"] == pred_line)
