from data_engine.core.base import BaseFilter
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import re, os
from tqdm import tqdm
from data_engine.utils.model_utils import get_model_path


class NlpFilterInstructionTags(BaseFilter):
    """
    指令数据集标签标注
    利用训练好的语言模型对指令数据集中的每一条指令进行分析和分类。语言模型可以根据指令的语义内容生成相应的标签。
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path: 大模型的名字或路径#用于加载大模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)

        self.ability_prompt = (
            "Please read the dialogue marked using ### between the user and an assistant, then enumerate what kind of abilities the assistant should use for completing this dialogue. Note that, only output the name of each kind of ability in Chinese, and seperate each kind of ability using <>. "
            "Note that do not output the meaningless ability name such as <问题解决>"
            "Note that you should distinguish 'ability' with 'knowledge'. For example, when providing a dialogue about code completion, you should output <编程能力>."
            "The following providing several instances:"
            "Dialogue：###USER: Given a string of text, return the first repeated word that appears in the string.\ntext = \"The quick brown fox jumps over the lazy dog. The dog barks at the fox.\"\nNote: Punctuation should not be considered as a part of a word.\nassistant: \"Here's a Python code that solves the problem:\n```\ndef first_repeated_word(text):\n    words = text.lower().replace('.', '').replace(',', '').split()\n    seen = set()\n    for word in words:\n        if word in seen:\n            return word\n        seen.add(word)\n    return None\n```\nHere's how to use the function:\n```\ntext = \"The quick brown fox jumps over the lazy dog. The dog barks at the fox.\"\nprint(first_repeated_word(text))  # Output: the\n```\nThe function first converts the text to lowercase and removes all punctuation. Then, it splits the text into a list of words. It uses a set to keep track of the words that have been seen before. For each word in the list, it checks if the word is already in the set. If it is, then it returns the word as the first repeated word. If the loop finishes without finding a repeated word, then it returns None.\n###\nWhat kind of abilities the assistant should have? Answer: "
            "<算法设计><字符串处理><集合操作><Python语法应用><代码注释能力><问题分解><边界条件处理><函数设计><代码优化><测试用例构建><代码解释>\n"
            "Dialogue：###USER: I walked 8 meters, which is only three-eighths of the total distance. How much further do I have to walk?\nASSISTANT: 8 meters is three-eighths of the total distance, which means the total distance is twenty-one and a third meters. Having walked 8 meters, there remains thirteen and a third meters to go.\n###What kind of abilities the assistant should have? Answer: "
            "<数学推理><符号推理><逻辑推理><分数计算><比例推理><单位换算><数学问题建模><步骤分解><结果验证>\n"
            "Dialogue：###USER: Who is Donald Trump?\nassistant: Donald Trump is an American businessman, television personality, and politician who served as the 45th President of the United States from January 20, 2017, to January 20, 2021. \n###\nWhat kind of abilities the assistant should have? Answer: "
            "<政治人物知识><美国总统历史><时间线记忆><公众人物背景概括><简洁信息提取>\n"
            "Dialogue：###USER: Please translate 'to paint the lily' into Chinese. \nassistant: The translation of 'to paint the lily' is “画蛇添足”.\n###\nWhat kind of abilities the assistant should have? Answer: "
            "<多语言理解><翻译><英语谚语理解><中英文化对比><成语匹配><语义等价转换><跨语言隐喻理解>\n"
            "Dialogue：###USER: 'Apples, oranges, bananas, sugarcane, strawberries, tomatoes, tangerines, pears, fruit' Please identify the item that differs from the others and explain the difference in detail.\nassistant: Among the options, 'fruit' differs from the others. 'Fruit' is a general category term, while the rest are names of individual species.\n###\nWhat kind of abilities the assistant should have? Answer: "
            "<逻辑推理><常识推理><类别识别><概念层级分析><集合理论应用><语义区分><归类推理>\n"
            "Dialogue：###USER：{}\n###\nWhat kind of abilities the assistant should have? Answer: "
        )
        self.llm_model = None

    def _reformat(self, dataset_ori):
        dat_tmp = dataset_ori
        prompt = ""
        for j in dat_tmp["content"]:
            if j["role"] == "user":
                prompt += "USER: " + j["content"] + "\n"
            else:
                prompt += "ASSISTANT: " + " ".join(j["content"].split()[-200:]) + "\n"

        prompt = " ".join(prompt.split(" ")[:400])
        dat_tmp["prompt"] = prompt

        return dat_tmp

    def _clean_tags(self, tag_string):
        tag_string = tag_string.split("\n")[-1]
        tags = re.split(r"[><]+", tag_string)
        tags = [t.strip().lower() for t in tags if t.strip()]
        tags = [re.sub(r"\s+", "", t) for t in tags]
        cleaned_tags = []
        for tag in tags:
            if len(tag) > 20:
                tag = re.sub(r"\d+\*\*|[*():]", "", tag)
                tag = re.sub(r"[\(\（][^\(\）\)]+[\)\）]", "", tag)
                tag = re.sub(r"[!]", "", tag)
                tag = re.sub(r"[^a-zA-Z\u4e00-\u9fff\s]", "", tag)
                tag = tag.strip()
            if tag and len(tag) < 20:
                cleaned_tags.append(tag)
        return cleaned_tags

    def process(self, data: dict):
        # 由于框架的限制，要求模型的载入需要process种完成，actor在处理第一个任务时完成模型载入
        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path, tensor_parallel_size=1, enforce_eager=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        data = self._reformat(data)

        prompt = self.ability_prompt.format(data["prompt"])
        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": prompt},
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        sampling_params = SamplingParams(
            max_tokens=2048,
            seed=42,
        )

        result = (
            self.llm_model.generate(formatted_prompt, sampling_params)[0]
            .outputs[0]
            .text
        )
        data["tags"] = self._clean_tags(result)

        data.pop("prompt")
        return data
