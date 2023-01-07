import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from typing import List
import ipdb

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(ROOT_DIR)
sys.path.append(BASE_DIR)
from pac import compute_k
from utils import utils


def create_plot_from_fn(
    x,
    y,
    save_path=f"{ROOT_DIR}/output",
    save_title="fn",
    xlabel=None,
    ylabel=None,
    title=None,
):
    _, ax = plt.subplots()
    plt.plot(x, y)
    ax.spines["right"].set_color((0.8, 0.8, 0.8))
    ax.spines["top"].set_color((0.8, 0.8, 0.8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # tweak the axis labels
    xlab = ax.xaxis.get_label()
    ylab = ax.yaxis.get_label()
    xlab.set_style("italic")
    xlab.set_size(10)
    ylab.set_style("italic")
    ylab.set_size(10)

    # tweak the title
    ttl = ax.title
    ttl.set_weight("bold")

    plt.tight_layout()
    plt.grid(linestyle="--", alpha=0.25)
    plt.savefig(f"{save_path}/{save_title}", bbox_inches="tight", transparent=False)


def plot_multiple_series(
    x: List,
    y: List,
    series_label: List[str],
    linestyle: List[str],
    color: List[str],
    title: str,
    xlabel: str,
    ylabel: str,
    save_title,
    line_width=None,
    save_path=f"{ROOT_DIR}/output",
):
    assert len(x) == len(y)
    assert len(x) == len(series_label)

    if line_width is None:
        line_width = [1] * len(x)
    assert len(x) == len(line_width)
    _, ax = plt.subplots()

    for i in range(len(x)):
        plt.plot(
            x[i],
            y[i],
            label=series_label[i],
            linewidth=line_width[i],
            linestyle=linestyle[i],
            color=color[i],
        )
    ax.spines["right"].set_color((0.8, 0.8, 0.8))
    ax.spines["top"].set_color((0.8, 0.8, 0.8))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # tweak the axis labels
    xlab = ax.xaxis.get_label()
    ylab = ax.yaxis.get_label()
    xlab.set_style("italic")
    xlab.set_size(10)
    ylab.set_style("italic")
    ylab.set_size(10)

    # tweak the title
    ttl = ax.title
    ttl.set_weight("bold")

    plt.legend()
    plt.tight_layout()
    plt.grid(linestyle="--", alpha=0.25)
    print(f"{save_path}/{save_title}")
    plt.savefig(f"{save_path}/{save_title}", bbox_inches="tight", transparent=False)


if __name__ == "__main__":
    # FROM DATA METHOD
    d = 0.1
    computed = []
    max_m = 4
    for m in range(1, max_m + 1):
        print("m", m, flush=True)
        data = []
        for q in range(90):
            print(q, flush=True)
            try:
                data += utils.read_json(
                    f"{ROOT_DIR}/results/optimize_output_ind_{q}__m_{m}.json"
                )["output"]
            except:
                pass
        print("retrieved data", len(data))
        map_tau_to_target_in_pruned_pred = {}
        map_tau_to_frac_rm = {}
        for sample in data:
            tau = np.exp(-1 * sample["cost"])
            if tau not in map_tau_to_target_in_pruned_pred:
                map_tau_to_target_in_pruned_pred[tau] = (0, 0)
                map_tau_to_frac_rm[tau] = []
            prev_cnt_sum = map_tau_to_target_in_pruned_pred[tau]
            # print("sample["target_in_pruned_pred"][0]", sample["target_in_pruned_pred"][0])
            map_tau_to_target_in_pruned_pred[tau] = (
                prev_cnt_sum[0] + int(sample["pred_in_target"]["eval"]),
                prev_cnt_sum[1] + 1,
            )
            map_tau_to_frac_rm[tau].append(sample["output"]["frac_included"])
        taus_lst = []
        coverage_lst = []
        frac_rm_lst = []
        n = -1
        for key in map_tau_to_target_in_pruned_pred:
            val = map_tau_to_target_in_pruned_pred[key]
            taus_lst.append(key)
            coverage_lst.append(val[0] / val[1] * 100)
            frac_rm_lst.append(100 - np.mean(map_tau_to_frac_rm[key]) * 100)
            n = val[1]
        assert len(taus_lst) == len(coverage_lst)
        assert len(taus_lst) == len(coverage_lst)
        assert len(taus_lst) == len(frac_rm_lst)

        # map data to e space
        e = np.linspace(0.03, 0.65, num=50).tolist()
        target_coverage = []
        for i in range(len(e)):
            print(n, e[i], d)
            target_coverage.append(100 - compute_k(n, e[i], d) / n * 100)

        e_to_taus_lst = []
        e_to_coverage_lst = []
        e_to_frac_rm_lst = []
        for i in range(len(e)):
            for j in range(len(taus_lst)):
                if coverage_lst[j] >= target_coverage[i]:
                    e_to_taus_lst.append(taus_lst[j])
                    e_to_coverage_lst.append(coverage_lst[j])
                    e_to_frac_rm_lst.append(frac_rm_lst[j])
                    break
        print("e", e)
        print("target_coverage", target_coverage)
        print("e_to_taus_lst", e_to_taus_lst)
        print("e_to_coverage_lst", e_to_coverage_lst)
        print("e_to_frac_rm_lst", e_to_frac_rm_lst)
        computed.append(
            {
                "e": e,
                "taus": e_to_taus_lst,
                "percent_nodes_removed": e_to_frac_rm_lst,
                "target_in_set": e_to_coverage_lst,
                "label": f"m={m}",
                "m": m,
                "linestyle": "-",
                "color": None,
            }
        )

    computed.append(
        {
            "e": e,
            "target_in_set": [100 - e_i * 100 for e_i in e],
            "label": "Target Bound",
            "linestyle": "--",
            "color": "black",
        }
    )
    os.makedirs(f"{ROOT_DIR}/output/", exist_ok=True)
    linewidths = list(range(1, 2 * (max_m + 1), 2))
    for key, y_label, title in [
        # ("taus", r"$\tau$", r"Satisfying $\tau$ For Given $\epsilon$"),
        # (
        #     "percent_nodes_removed",
        #     "Percentage of Nodes Removed (%)",
        #     r"Percent Nodes Removed Over $\epsilon$ Space",
        # ),
        (
            "target_in_set",
            "Percentage of Satisfying Code Sets (%)",
            r"Percent Code Set Coverage Over $\epsilon$ Space",
        ),
    ]:
        print("Creating plots", key, y_label, title, flush=True)
        plot_multiple_series(
            [computed[i]["e"] for i in range(len(computed))],
            [computed[i][key] for i in range(len(computed))],
            [computed[i]["label"] for i in range(len(computed))],
            [computed[i]["linestyle"] for i in range(len(computed))],
            [computed[i]["color"] for i in range(len(computed))],
            title,
            r"$\epsilon$",
            y_label,
            key,
            # line_width=[linewidths[computed[i]["m"]-1] for i in range(len(computed))]
        )
