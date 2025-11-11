from data_engine.core.base import BaseFilter
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
import re
from tqdm import tqdm
from data_engine.utils.model_utils import get_model_path


class NlpFilterHierarchicalTags(BaseFilter):
    """
    分级标签系统构建
    建立分级标签系统，便于对文本进行层次分类并应用于之后的数据筛选。
    后训练数据合成专用算法
    """

    use_class = True  # 由于处理中用到模型，use_class = True，使用ray actor模式，避免模型重复加载

    def __init__(self, model_name_or_path: str, **kwargs):
        """
        初始化方法：
            model_name_or_path: 大模型的名字或路径#用于加载模型
        """
        super().__init__(**kwargs)
        self.model_name_or_path = get_model_path(model_name_or_path)
        self.meta_categories_prompt = """
            请依据现有的标签,判断属于以下标签中的一种或几种:\n
            ['故事理解','编程能力', '开放知识问答', '情感分析', '创意与设计', '文学创作与艺术知识', 'STEM知识', '文本理解', '数学计算', '教育与咨询', '常识推理', '数学推理', '文本摘要', '信息抽取', '自然语言理解', '文本生成', '财务、金融与商业知识', '知识理解', 'python编程', '任务生成', '技术理解', '沟通与社交媒体', '信息整合', '对话理解', '阅读理解', '推理能力', '人文历史哲学与社会学知识', '情境理解', '语言学知识、多语言与多元文化理解', '知识推理', '心理学知识', '数据解析', '信息组织', '对话管理', '多轮对话', '推荐系统', '数学建模', '算术计算', 'javascript编程', '生活知识与技能', '数据分析', '事件理解', '字符串处理', '事件描述', '信息提供', '分析与研究', '问题理解', '编程知识', 'java编程', '情节理解', '常识理解', '分类能力', '数学知识', '算法分析', '数据处理', '人物理解', '算法设计', '列表生成', '文本组织', '文本分类', '编码能力', '逻辑组织', '翻译','字符理解', '学术写作','概念理解']\n
            标签之间以"###"分割，注意不要返回任何多余的内容，若没有则返回None。\n
            例如：\n
            输入：文本生成###信息抽取###文章写作\n
            返回：文本生成###信息抽取\n
            输入：{}\n
            返回：
            """
        self.llm_model = None

    def process(self, data: dict):
        # 由于框架的限制，要求模型的载入需要process种完成，actor在处理第一个任务时完成模型载入
        if not self.llm_model:
            self.llm_model = LLM(
                self.model_name_or_path, tensor_parallel_size=1, enforce_eager=True
            )  # 载入模型
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        label = [
            "故事理解",
            "编程能力",
            "开放知识问答",
            "情感分析",
            "创意与设计",
            "文学创作与艺术知识",
            "STEM知识",
            "文本理解",
            "数学计算",
            "教育与咨询",
            "常识推理",
            "数学推理",
            "文本摘要",
            "信息抽取",
            "自然语言理解",
            "文本生成",
            "财务、金融与商业知识",
            "知识理解",
            "python编程",
            "任务生成",
            "技术理解",
            "沟通与社交媒体",
            "信息整合",
            "对话理解",
            "阅读理解",
            "推理能力",
            "人文历史哲学与社会学知识",
            "情境理解",
            "语言学知识、多语言与多元文化理解",
            "知识推理",
            "心理学知识",
            "数据解析",
            "信息组织",
            "对话管理",
            "多轮对话",
            "推荐系统",
            "数学建模",
            "算术计算",
            "javascript编程",
            "生活知识与技能",
            "数据分析",
            "事件理解",
            "字符串处理",
            "事件描述",
            "信息提供",
            "分析与研究",
            "问题理解",
            "编程知识",
            "java编程",
            "情节理解",
            "常识理解",
            "分类能力",
            "数学知识",
            "算法分析",
            "数据处理",
            "人物理解",
            "算法设计",
            "列表生成",
            "文本组织",
            "文本分类",
            "编码能力",
            "逻辑组织",
            "翻译",
            "字符理解",
            "学术写作",
            "概念理解",
        ]
        prompt = self.meta_categories_prompt.format("###".join(data["tags_norm"]))
        messages = [
            {"role": "system", "content": "You are a helpful and concise assistant."},
            {"role": "user", "content": prompt},
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        sampling_params = SamplingParams(
            max_tokens=1024,
            seed=42,
        )
        result = (
            self.llm_model.generate(formatted_prompt, sampling_params)[0]
            .outputs[0]
            .text
        )
        result = result.strip().split("：")[-1]
        array = []
        for item in result.split("###"):
            item = item.strip()
            if item in label:
                array.append(item)
        data["tags_label"] = array

        return data
