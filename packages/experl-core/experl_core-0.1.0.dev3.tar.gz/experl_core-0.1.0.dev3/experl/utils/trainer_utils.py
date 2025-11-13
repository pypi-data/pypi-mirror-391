import argparse
import datetime
import os
import re
import socket
from pathlib import Path

import torch
from transformers import AutoTokenizer

from experl.config.schema.config_classes import OrchestratorConfig
from experl.utils.logging_utils import get_logger


log = get_logger(__name__)


def generate_responses(model_ref, tokenizer_ref, prompts, max_new_tokens):
    inputs = tokenizer_ref(prompts, return_tensors="pt", padding=True).to(
        model_ref.device
    )
    outputs = model_ref.generate(**inputs, max_new_tokens=max_new_tokens)
    return tokenizer_ref.batch_decode(outputs, skip_special_tokens=True)


def get_tracking_path(orch_config) -> str:
    tracking_path = Path(os.path.join(orch_config.root_dir, "mlflow_runs"))
    tracking_path.mkdir(parents=True, exist_ok=True)
    return str(tracking_path)


def create_file_path(orch_config: OrchestratorConfig, output_fle: str):
    return str(
        os.path.join(
            orch_config.run_base_dir,
            f"{output_fle}",
        )
    )


def get_tokenizer(model_id: str, padding_side: str = None):
    tokenizer_obj = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    if padding_side is not None:
        tokenizer_obj.padding_side = padding_side

    return tokenizer_obj


def get_tokenizer_config(tokenizer_ref) -> dict:
    tokenizer_config = {
        "name_or_path": tokenizer_ref.name_or_path,
        "padding_side": tokenizer_ref.padding_side,
        "truncation_side": tokenizer_ref.truncation_side,
        "model_max_length": tokenizer_ref.model_max_length,
        "vocab_size": len(tokenizer_ref),
    }
    return tokenizer_config


def generate_run_name(
    base_name: str,
    task: str = None,
    tag: str = None,
    include_timestamp: bool = True,
    include_host: bool = False,
) -> str:
    parts = [get_model_id(base_name)]
    if task:
        parts.append(task)
    if tag:
        parts.append(tag)
    if include_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        parts.append(timestamp)
    if include_host:
        hostname = socket.gethostname().split(".")[0]
        parts.append(hostname)
    return "__".join(parts)


def parse_cli_args():
    """
    Parse only the meta-level arguments before Hydra takes control.
    All `++` arguments will be handled by Hydra automatically.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-name",
        type=str,
        default="ppo",
        help="Hydra config name (without .yaml)",
    )
    cli_args, overrides = parser.parse_known_args()

    filtered_overrides = []
    skip_next = False
    for _, arg in enumerate(overrides):
        if arg in ("--config-name",):
            skip_next = True
            continue
        elif skip_next:
            skip_next = False
            continue
        filtered_overrides.append(arg)

    log.info(f"CLI Args : {cli_args}")
    log.info(f"Hydra Overrides : {filtered_overrides}")
    return cli_args, filtered_overrides


def print_tokenizer_details(name, tokenizer_ref) -> None:
    log.debug(f"{name} - tokenizer - padding_side: {tokenizer_ref.padding_side}")
    log.debug(f"{name} - tokenizer - PAD token: {tokenizer_ref.pad_token}")
    log.debug(f"{name} - tokenizer - PAD token ID: {tokenizer_ref.pad_token_id}")
    log.debug(f"{name} - tokenizer - EOS token: {tokenizer_ref.eos_token}")
    log.debug(f"{name} - tokenizer - EOS token ID: {tokenizer_ref.eos_token_id}")


def get_model_id(model_name_or_path: str) -> str:
    """Converts a model ID into a safe directory name."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", model_name_or_path)


def sanitize_model(model_ref, tokenizer_ref):
    try:
        log.debug(f"tokenizer - bos_token {tokenizer_ref.bos_token}")
        log.debug(f"tokenizer - eos_token {tokenizer_ref.eos_token}")
        log.debug(f"tokenizer - pad_token {tokenizer_ref.pad_token}")

        if hasattr(model_ref.config, "bos_token"):
            log.debug(f"model - bos_token {model_ref.config.bos_token}")
        if hasattr(model_ref.config, "eos_token"):
            log.debug(f"model - eos_token {model_ref.config.eos_token}")
        if hasattr(model_ref.config, "pad_token"):
            log.debug(f"model - pad_token {model_ref.config.pad_token}")

        if tokenizer_ref.pad_token is None:
            tokenizer_ref.pad_token = tokenizer_ref.eos_token
            model_ref.config.pad_token_id = tokenizer_ref.eos_token_id
            model_ref.config.eos_token_id = tokenizer_ref.eos_token_id

        tokenizer_length = len(tokenizer_ref)
        if len(tokenizer_ref) != model_ref.config.vocab_size:
            model_ref.resize_token_embeddings(tokenizer_length)
            log.info(
                f"resized embeddings for {model_ref.__class__.__name__} to {tokenizer_length}"
            )
        return model_ref, tokenizer_ref
    except Exception as e:
        log.error(f"Exception in the sanitize_model : {e}")


def get_device() -> str:
    if torch.cuda.is_available():
        log.debug("CUDA (GPU) is available. Using the GPU.")
        return "cuda"
    else:
        log.debug("CUDA (GPU) is not available. Using the CPU.")
        return "cpu"


def get_dtype(dtype: str) -> torch.dtype:
    return dtype if dtype in ["auto", None] else getattr(torch, dtype)
