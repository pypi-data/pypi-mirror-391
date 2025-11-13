# 🧠 Experl — RLHF Framework for Post-Training Large Language Models

---

## 📜 Overview

Experl is a framework designed for post-training large language and foundation models using Reinforcement Learning from Human Feedback (RLHF) techniques such as Proximal Policy Optimization (PPO) and Direct Preference Optimization (DPO).

Built on top of Hugging Face TRL and Transformers, Experl provides a flexible and extensible platform for training, evaluation, and experimentation in RLHF-based fine-tuning workflows.
It integrates seamlessly with:

- 🤗 TRL – provides trainer abstractions for RL pipelines
- 🤗 Transformers – for model and tokenizer management
- ⚙️ Hydra – for structured and hierarchical configuration management
- 📊 MLflow – used for training experiment tracking, metrics logging, datasets and model versioning


Experl simplifies the complex process of RLHF post-training, allowing researchers and engineers to focus on experimentation, comparison, and innovation — rather than boilerplate code.

---
## 🚀 Getting Started

## Installation

### Python Package

Install the library using `pip`:

```bash
pip install experl
```

### From source

If you want to use the latest features before an official release, you can install Experl from source:

```bash
pip install git+https://github.com/vjkhambe/experl.git
```

### Repository

If you want to use the examples you can clone the repository with the following command:

```bash
git clone https://github.com/vjkhambe/experl.git
```
---

## Command Line Interface (CLI)

You can use the Experl Command Line Interface (CLI) to quickly get started with post-training methods like Proximal Policy Optimization (PPO) or Direct Preference Optimization (DPO):

**PPO:**

```bash
experl ppo \
++model_name_or_path=google/gemma-3-270m-it \
++project.max_seq_length=128 \
++ppo.reward_model_name_or_path=google/gemma-3-270m-it
```

**DPO:**

```bash
experl dpo \
++model_name_or_path=google/gemma-3-270m-it \
++project.max_seq_length=128
```

## Citation

```bibtex
@misc{vjkhambe2025experl,
  author = {Vijay Khambe},
  title = {Experl: Reinforcement Learning from Human Feedback Framework},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/vjkhambe/experl}}
}
```

## License

This repository's source code is available under the [Apache-2.0 License](LICENSE).