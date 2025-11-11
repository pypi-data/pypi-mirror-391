from .config import default_induct_instruct, default_summarize_instruct, default_pattern
import json
import random
from openai import OpenAI
from tqdm import tqdm


def readjsonl(filename):
    with open(filename, encoding="utf8") as f:
        datas = f.readlines()
    datas_tmp = []
    for data in datas:
        data = json.loads(data)
        datas_tmp.append(data)
    return datas_tmp


def getids(todir):
    ids, l = [], []
    datas = readjsonl(todir)
    num = 0
    for data in datas:
        if type(data) == int:
            num = 0
            l.append(data)
        else:
            if num % 2 == 0:
                ids.append(data)
            num += 1
    return ids, l


def getbiasinfo(s, template):
    if template in s:
        start = 0
        position = s.find(template, start)
        tmp = position
        for i in range(position, -1, -1):
            if s[i] == "\n":
                tmp = i
                break
        return s[tmp + 1 : position].lstrip('"').lstrip("- ") + template
    return None


def getbias(fromdir, template):
    datas = readjsonl(fromdir)
    num = 0
    bias = {}
    pre = -1
    for data in datas:
        if type(data) == int:
            bias[data] = []
            pre = data
            num = 0
            continue
        if num % 2 == 1:
            if template in data:
                bias[pre].append(getbiasinfo(data, template))
        num += 1
    return bias


class BiasInductionEngine:
    def __init__(self, client, group_size=5):
        self.model_name = client
        self.group_size = group_size
        self.callclient = client

    def callclient(self, message, pattern):
        message = [{"role": "user", "content": message}]
        chat_response = self.client.chat.completions.create(
            model=self.induct_model_name, temperature=0, messages=message
        )
        reply = json.loads(chat_response.json())["choices"][0]["message"]["content"]
        stop_num = 5
        while stop_num > 0 and pattern not in reply:
            chat_response = self.client.chat.completions.create(
                model=self.induct_model_name, temperature=0.5, messages=message
            )
            reply = json.loads(chat_response.json())["choices"][0]["message"]["content"]
            stop_num -= 1
        return reply

    def induct(self, max_samples=500, seed=0):
        random.seed(seed)

        if len(datas) > max_samples:
            datas = random.sample(datas, max_samples)
        else:
            datas = datas[: len(datas) // self.group_size * self.group_size]
        prompt = ""
        num = 0
        reply_ls = []
        for i, data in tqdm(enumerate(datas)):
            num += 1
            if num <= self.group_size:
                prompt += (
                    "\n<counter example pair "
                    + str(num)
                    + ">\nExample 1: "
                    + data[0][0]
                    + "\ngold: "
                    + data[0][1]
                    + ". predicted: "
                    + data[0][2]
                    + ".\nExample 2: "
                    + data[1][0]
                    + "\ngold: "
                    + data[1][1]
                    + ". predicted: "
                    + data[1][2]
                    + ".\n"
                )
            if num == self.group_size:
                message = self.induct_instruct + prompt
                reply = self.callclient(message, self.pattern)
                reply_ls.append(reply)
        print("induct finished")
        self.reply_ls = reply_ls
        return reply_ls

    def summarize(
        self,
    ):
        bias = self.reply_ls
        bias_pattterns = []
        for key in bias.keys():
            print(key)
            num = 1
            prompt = ""
            for i, bia in enumerate(bias[key]):
                prompt += "sentence " + str(num) + ": " + bia + ".\n"
                num += 1

            message = self.summarize_instruct + prompt
            chat_response = self.client.chat.completions.create(
                model=self.induct_model_name,
                temperature=0,
                messages=[{"role": "user", "content": message}],
            )
            reply = json.loads(chat_response.json())["choices"][0]["message"]["content"]
            print(reply)
            bias_pattterns.append(reply)
        return bias_pattterns
