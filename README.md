# PAC Prediction Sets for Large Language Models of Code
Adam Khakhar, Stephen Mell, Osbert Bastani\
[arXiv](https://arxiv.org/abs/2302.08703)
## Citation Information:
```
@misc{khakhar2023pac,
      title={PAC Prediction Sets for Large Language Models of Code}, 
      author={Adam Khakhar and Stephen Mell and Osbert Bastani},
      year={2023},
      eprint={2302.08703},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```

## Getting Started
1. Create prompt and solution (humaneval_dataset_interface.py)
2. Get prediction (codex_interface.py, inference.py)
3. Parse results into AST (parse_results.py, ast_helper.py)
4. Compute optimization (optimize.py, optimize_greedy.py)
5. Evaluate and create plots (create_plots.py)