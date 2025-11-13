import torch
from vllm import LLM, SamplingParams
from vllm.sequence import SequenceData, SequenceGroupMetadata
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from config import (
    Default_prefix,
    Default_prelen,
    Default_remove_prefix,
    Default_remove_suffix,
    LABEL_SPACE,
)
from tqdm import tqdm
import numpy as np
import json


def write_jsonl(file, train_datas):
    with open(file, "w", encoding="utf-8") as f:
        for data in train_datas:
            json.dump(data, f, ensure_ascii=False)
            f.write("\n")


class InferenceEngine:
    def __init__(self, model, tokenizer, dataset_type):
        self.dataset_type = dataset_type
        self.label_space = LABEL_SPACE[dataset_type]
        self.model = model
        self.tokenizer = tokenizer

    def getlabelrep(self, prefix, return_type="token"):
        self.tokenizer.padding_side = "right"
        length = self.tokenizer(
            [prefix + label_space for label_space in self.label_space],
            padding=False,
            return_length=True,
        )["length"]
        length = max(length)
        label_spaces_ids = self.tokenizer(
            [prefix + label_space for label_space in self.label_space],
            padding="max_length",
            max_length=length,
            return_tensors="pt",
        )["input_ids"]
        self.tokenizer.padding_side = "left"
        if return_type == "token":
            return [
                self.tokenizer.convert_ids_to_tokens(label_spaces_ids[i])
                for i in range(len(label_spaces_ids))
            ]
        elif return_type == "ids":
            return label_spaces_ids
        else:
            raise ("illegal return type")

    def process_input(self, raw_data, prefix, prelen):
        input_text = raw_data["content"]
        label = raw_data["label"]
        label_spaces = self.label_space

        self.tokenizer.padding_side = "right"
        length = self.tokenizer(
            [prefix + label_space for label_space in label_spaces],
            padding=False,
            return_length=True,
        )["length"]
        length = max(length)
        label_spaces_ids = self.tokenizer(
            [prefix + label_space for label_space in label_spaces],
            padding="max_length",
            max_length=length,
            return_tensors="pt",
        )["input_ids"]
        self.tokenizer.padding_side = "left"
        # import pdb
        # pdb.set_trace()
        label_spaces_ids = torch.tensor(label_spaces_ids, dtype=torch.int32).to("cuda")
        # label_spaces_ids = label_spaces_ids[:, prelen:]

        return input_text, label, label_spaces_ids

    def inference(self, raw_data, data_type):
        # These two pieces of data are too long, so remove these two pieces of data

        id2label = dict()
        for i, label in enumerate(self.label_space):
            id2label[i] = label

        example = {}

        example["gold"] = raw_data["label"]
        candidate_ls = [raw_data["content"] + " " + label for label in self.label_space]
        device = "cuda" if torch.cuda.is_available() else "cpu"

        inputs = self.tokenizer(candidate_ls, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        outputs = self.model(**inputs)

        embeddings = outputs.hidden_states[-1][0][-2, :].cpu().tolist()
        logits = outputs.logits
        softmax_logits = torch.nn.functional.softmax(logits, dim=-1)

        scores = []
        for s, i in zip(softmax_logits, inputs["input_ids"]):
            score = [s[k, i[k]].item() for k in range(len(i))]
            scores.append(sum(score))

        scores = torch.FloatTensor(scores)
        pred = torch.argmax(scores, dim=-1).item()

        # For Influential Criterion:
        # The greater the loglikelihood probability of a gold answer compared to a predicted answer, the greater the
        # impact of bias information on LLM. Because the loglikelihood probability is negative, the expression
        # for the degree to which log(P(gold)) is greater than log(P(pred)) is log(P(pred))/log(P(gold))
        gold_score = (
            scores[self.label_space.index(example["gold"])].item() / scores[pred].item()
        )
        example["pred"] = id2label[pred]
        example["gold_score"] = gold_score
        example["representations"] = embeddings
        example["content"] = raw_data["content"]
        example["candidate_ans"] = self.label_space

        return example
