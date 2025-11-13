import json

import torch
from tqdm import tqdm

from experl.config.schema.config_classes import OrchestratorConfig
from experl.evaluation.evaluator import EvaluationResult
from experl.utils.dataset_utils import batch_iter
from experl.utils.trainer_utils import generate_responses


class RewardJudgeEvaluator:
    def __init__(
        self,
        reference_model,
        candidate_model,
        reward_model,
        reference_tokenizer,
        reward_tokenizer,
        config: OrchestratorConfig,
        result_file_path: str,
    ):
        self.reward_model = reward_model
        self.reference_model = reference_model
        self.candidate_model = candidate_model
        self.reference_tokenizer = reference_tokenizer
        self.reward_tokenizer = reward_tokenizer
        self.config = config
        self.result_file_path = result_file_path

    def evaluate(self, dataset, batch_size) -> EvaluationResult:
        results = []
        wins = 0
        ties = 0
        losses = 0
        with open(self.result_file_path, "w") as file:
            for batch in tqdm(batch_iter(dataset, batch_size)):
                prompts = batch["prompt"]
                base_responses = generate_responses(
                    self.reference_model,
                    self.reference_tokenizer,
                    prompts,
                    self.config.ppo.eval.max_new_tokens,
                )
                dpo_responses = generate_responses(
                    self.candidate_model,
                    self.reference_tokenizer,
                    prompts,
                    self.config.ppo.eval.max_new_tokens,
                )

                for prompt, base_resp, ppo_resp in zip(
                    prompts, base_responses, dpo_responses, strict=False
                ):
                    sft_score = self._reward_model_score(f"{prompt} {base_resp}")
                    ppo_score = self._reward_model_score(f"{prompt} {ppo_resp}")

                    winner = "tie"
                    if ppo_score > sft_score:
                        winner = "ppo_model"
                        wins += 1
                    elif sft_score > ppo_score:
                        winner = "base_model"
                        losses += 1
                    else:
                        ties += 1
                    result_item = {
                        "prompt": prompt,
                        "base_model_response": base_resp,
                        "ppo_model_response": ppo_resp,
                        "base_model_score": sft_score,
                        "ppo_model_score": ppo_score,
                        "winner": winner,
                    }
                    results.append(result_item)
                    file.write(json.dumps(result_item) + "\n")

        total = len(results)
        metrics = {
            "eval/judge_win_rate": wins / total,
            "eval/judge_tie_rate": ties / total,
            "eval/judge_loss_rate": losses / total,
        }
        return EvaluationResult(wins, losses, ties, total, results, metrics)

    def _reward_model_score(self, text: str) -> str:
        inputs = self.reward_tokenizer(
            text, return_tensors="pt", truncation=True, padding=True
        ).to(self.reward_model.device)

        with torch.no_grad():
            _rewards = self.reward_model.get_reward(**inputs).squeeze(-1)
        if _rewards.numel() == 1:
            score = _rewards.item()
        else:
            raise ValueError(f"Expected scalar tensor, got shape {_rewards.shape}")
        return score
