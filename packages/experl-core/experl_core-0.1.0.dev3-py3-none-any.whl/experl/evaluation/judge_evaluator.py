import json

import torch
from tqdm import tqdm

from experl.config.schema.config_classes import OrchestratorConfig
from experl.evaluation.evaluator import EvaluationResult
from experl.utils.dataset_utils import batch_iter
from experl.utils.logging_utils import get_logger
from experl.utils.trainer_utils import generate_responses


log = get_logger(__name__)


class DPOJudgeEvaluator:
    def __init__(
            self,
            reference_model,
            candidate_model,
            judge_model,
            reference_tokenizer,
            judge_tokenizer,
            config: OrchestratorConfig,
            result_file_path: str,
    ):
        self.judge_model = judge_model
        self.reference_model = reference_model
        self.candidate_model = candidate_model
        self.reference_tokenizer = reference_tokenizer
        self.judge_tokenizer = judge_tokenizer
        self.config = config
        self.result_file_path = result_file_path

    def evaluate(self, dataset, batch_size) -> EvaluationResult:
        results = []
        with open(self.result_file_path, "w") as file:
            for batch in tqdm(batch_iter(dataset, batch_size)):
                prompts = batch["prompt"]
                base_responses = generate_responses(
                    self.reference_model,
                    self.reference_tokenizer,
                    prompts,
                    self.config.dpo.eval.max_new_tokens,
                )
                dpo_responses = generate_responses(
                    self.candidate_model,
                    self.reference_tokenizer,
                    prompts,
                    self.config.dpo.eval.max_new_tokens,
                )

                for prompt, base_resp, dpo_resp in zip(
                    prompts, base_responses, dpo_responses, strict=False
                ):
                    judge_input = self.config.dpo.judge.prompt_template.format(
                        prompt=prompt, response_a=base_resp, response_b=dpo_resp
                    )
                    verdict = self._query_judge(judge_input)
                    result_item = {
                        "prompt": prompt,
                        "base_model_response": base_resp,
                        "dpo": dpo_resp,
                        "verdict": verdict,
                    }
                    results.append(result_item)
                    file.write(json.dumps(result_item) + "\n")

        wins = sum(1 for r in results if r["verdict"] == "B")
        losses = sum(1 for r in results if r["verdict"] == "A")
        ties = sum(1 for r in results if r["verdict"].lower().startswith("tie"))
        total = len(results)
        metrics = {
            "eval/judge_win_rate": wins / total,
            "eval/judge_tie_rate": ties / total,
            "eval/judge_loss_rate": losses / total,
        }

        return EvaluationResult(wins, losses, ties, total, results, metrics)

    def _query_judge(self, text: str) -> str:
        """
        Query local judge model using transformers pipeline or raw generation.
        The judge model should output a short text like 'A', 'B', or 'Tie'.
        """
        inputs = self.judge_tokenizer(
            text, return_tensors="pt", truncation=True, padding=True
        ).to(self.judge_model.device)

        with torch.no_grad():
            outputs = self.judge_model.generate(
                **inputs,
                max_new_tokens=5,
                temperature=self.config.dpo.judge.temperature,
                do_sample=False,
                pad_token_id=self.judge_tokenizer.eos_token_id,
            )

        response = self.reference_tokenizer.decode(outputs[0], skip_special_tokens=True)
        verdict = response.strip().split()[-1]
        return extract_answer(verdict)


def extract_answer(input_string: str) -> str:
    if input_string:
        cleaned_string = input_string.replace("\\", "").replace('"', "")
        return cleaned_string
    return input_string
