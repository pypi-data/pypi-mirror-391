import json
import datasets
from tqdm import tqdm
import pdb

# from .config import NLI_PROMPT, BIAS_PROMPT, MT_bench_PROMPT, prompt_raw, LABEL_SPACE
BIAS_PROMPT = "Context: {}\nQ: {}\nOptions:\nA: {} B: {} C: {}\nAnswer:\n"


def readjsonl(filename):
    with open(filename, encoding="utf8") as f:
        datas = f.readlines()
    datas_tmp = []
    for data in datas:
        data = json.loads(data)
        datas_tmp.append(data)
    return datas_tmp


class Dataset:
    def __init__(self, data_path, label_space, id2label, prompt=BIAS_PROMPT):
        datas = readjsonl(data_path)
        self.data = []
        self.id2label = id2label
        self.label_space = label_space
        for data in tqdm(datas):
            context = data["context"]
            question = data["question"]
            ans_key_ls = [k for k in data.keys() if "ans" in k]
            ans_key_ls = sorted(ans_key_ls, key=lambda x: int(x.replace("ans", "")))
            all_choices = [data[k] + "." for k in ans_key_ls]
            # all_choices=[data['ans0']+'.',data['ans1']+'.',data['ans2']+'.']
            label = data["label"]
            self.data.append(
                {
                    "content": prompt.format(
                        context,
                        question,
                        all_choices[0],
                        all_choices[1],
                        all_choices[2],
                    ),
                    "label": self.id2label[label],
                    "label_space": label_space,
                }
            )

    def __len__(self):
        assert self.data is not None, "self.data is None. Please load data first."
        return len(self.data)

    def get_content_by_idx(self, idx, task=None):
        return self.data[idx]


def create_dataset(label_space, data_dir, prompt):
    # label_space: None, list

    id2label = dict()
    if label_space != "undetermined":
        for i, label in enumerate(label_space):
            id2label[i] = label

    return Dataset(data_dir, label_space, id2label, prompt)
