from typing import Any

import torch
from torch import nn
from transformers import AutoModel, PreTrainedModel


class RewardModel(PreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.base_model_prefix = "model"
        self.model = AutoModel.from_config(config)
        self.value_head = nn.Linear(config.hidden_size, 1)
        self.value_head = self.value_head.to(self.model.dtype)
        self.post_init()

    def forward(
        self,
        input_ids_chosen: torch.LongTensor,
        attention_mask_chosen: torch.LongTensor = None,
        input_ids_rejected: torch.LongTensor = None,
        attention_mask_rejected: torch.LongTensor = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        The forward pass of the RewardModel.

        Args (what the Trainer provides):
            input_ids_chosen: Token IDs for the preferred/chosen text.
            attention_mask_chosen: Attention mask for the chosen text.
            input_ids_rejected: Token IDs for the rejected text.
            attention_mask_rejected: Attention mask for the rejected text.
        """

        rewards_chosen = self.get_reward(
            input_ids=input_ids_chosen,
            attention_mask=attention_mask_chosen,
            **kwargs,
        )
        rewards_rejected = self.get_reward(
            input_ids=input_ids_rejected,
            attention_mask=attention_mask_rejected,
            **kwargs,
        )

        margin = rewards_chosen - rewards_rejected
        loss = -torch.nn.functional.logsigmoid(margin).mean()
        return {
            "loss": loss,
            "chosen_reward": rewards_chosen,
            "rejected_reward": rewards_rejected,
        }

    def get_reward(
        self, input_ids=None, attention_mask=None, hidden_states=None, **kwargs
    ):

        if hidden_states is not None:
            outputs = self.model(
                inputs_embeds=hidden_states,
                attention_mask=attention_mask,
                output_hidden_states=True,
                **kwargs,
            )
        else:
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                **kwargs,
            )
        hidden = outputs.last_hidden_state
        if attention_mask is not None:
            last_token_idx = attention_mask.sum(dim=1) - 1
            last_hidden = hidden[torch.arange(hidden.size(0)), last_token_idx]
        else:
            last_hidden = hidden[:, -1]

        return self.score(last_hidden)

    def score(self, last_hidden: torch.Tensor) -> torch.Tensor:
        reward_score = self.value_head(last_hidden).squeeze(-1)
        reward_score = torch.tanh(reward_score)
        return reward_score

    def get_input_embeddings(self):
        return self.model.get_input_embeddings()
