import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import hydra
import mlflow
import psutil
import torch
import transformers
import trl
from trl.scripts.utils import get_git_commit_hash

from experl.utils.logging_utils import get_logger


log = get_logger(__name__)




def get_file_text(file_path: str, max_lines: int = 100) -> str:
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line)
        return "".join(lines).strip()
    except FileNotFoundError as ex:
        log.error(f"File not found: {file_path} — {ex}")
        raise ex
    except Exception as ex:
        log.error(f"Error reading file: {file_path} — {ex}")
        raise ex


def _compute_file_hash(file_path: Path, hash_func=hashlib.md5) -> str:
    hasher = hash_func()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _generate_dataset_version(
        dataset_path: Path, tokenizer_config: dict[str, Any] | None = None
) -> str:
    """Generate a deterministic dataset version string from hash + tokenizer info."""
    try:
        dataset_hash = _compute_file_hash(dataset_path)
        tokenizer_hash = None
        if tokenizer_config:
            encode_text = json.dumps(tokenizer_config, sort_keys=True).encode()
            tokenizer_hash = hashlib.md5(encode_text).hexdigest()

        combined = f"{dataset_hash[:8]}-{tokenizer_hash[:8] if tokenizer_hash else 'no_tokenizer'}"
        return combined
    except Exception as ex:
        log.error(f"Error while generating dataset version : {dataset_path} — {ex}")


def get_sys_info():
    sys_info = {
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "trl_version": getattr(trl, "__version__", "N/A"),
        "hydra_version": getattr(hydra, "__version__", "N/A"),
        "mlflow_version": getattr(mlflow, "__version__", "N/A"),
        "commit_hash": (get_git_commit_hash("experl")),
        "os": platform.platform(),
        "hostname": platform.node(),
    }
    return sys_info


def _get_project_root(marker="experl"):
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker).is_dir():
            return parent
    raise FileNotFoundError(
        f"Project root could not be found. Searched for a directory containing '{marker}'."
    )


def exists(file_path: str) -> bool:
    return Path(file_path).exists()


if __name__ == "__main__":
    commit = get_git_commit_hash(str(_get_project_root()))
    log.info(f"commit hash = {commit}")


