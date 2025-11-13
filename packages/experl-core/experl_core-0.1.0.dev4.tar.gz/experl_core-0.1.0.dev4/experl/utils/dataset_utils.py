from datetime import datetime

from datasets import Dataset

from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import get_tokenizer_config


log = get_logger(__name__)


def batch_iter(dataset, batch_size):
    for ind in range(0, len(dataset), batch_size):
        yield dataset[ind: ind + batch_size]


def get_dataset_metadata(dataset,
                         tokenizer_ref,
                         max_samples: int = 5,
                         name: str = "train",
                         log_preview: bool = True,
                         log_stats: bool = True,
                         log_full: bool = False,
                         exclude_token_tensors: bool = True) -> dict:
    tokenizer_config = get_tokenizer_config(tokenizer_ref)

    if isinstance(dataset, Dataset):
        num_rows = len(dataset)
        columns = dataset.column_names
        preview = dataset.select(range(min(max_samples, num_rows)))
        preview_dict = preview.to_dict()

    # Compute simple stats
    token_stats = {}
    if "input_ids" in columns:
        avg_len = (
            sum(len(x) for x in dataset["input_ids"]) / len(dataset["input_ids"])
            if len(dataset["input_ids"]) > 0
            else 0
        )
        token_stats[f"dataset.{name}.avg_tokens"] = avg_len

    metadata = {
        # "file_name": dataset.name,
        "dataset_name": name,
        "num_rows": num_rows,
        "columns": columns,
        # "hash": _compute_file_hash(dataset_path),
        # "dataset_version": _generate_dataset_version(dataset_path, tokenizer_config),
        "created_at": datetime.now().isoformat(),
        "preview_dict": preview_dict,
        **token_stats,
        f"dataset.{name}.columns": ", ".join(columns),
        f"dataset.{name}.type": type(dataset).__name__,
        f"dataset.{name}.num_rows": num_rows,
        f"dataset.{name}.num_columns": len(columns),
    }
    if tokenizer_config:
        metadata["tokenizer"] = tokenizer_config
    return metadata
