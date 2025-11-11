from copy import deepcopy
from loguru import logger
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.char as nac
import nlpaug.flow as naf
from nlpaug.util import Action
from data_engine.core.base import BaseMapper


class NlpMapperEnglishTextAugment(BaseMapper):
    """
    英文文本增强映射器
    用于对单条英文文本样本进行数据增强，支持多种基于 nlpaug 的单词级和字符级增强方式。增强方式可按顺序组合或并行执行，生成多个增强版本，用于提升模型的鲁棒性和泛化能力。
    """

    def __init__(
        self,
        use_sequential_pipeline: bool = False,
        num_augmentations: int = 1,
        enable_word_delete: bool = False,
        enable_word_swap: bool = False,
        enable_word_spelling: bool = False,
        enable_word_split: bool = False,
        enable_char_keyboard: bool = False,
        enable_char_ocr: bool = False,
        enable_char_delete: bool = False,
        enable_char_swap: bool = False,
        enable_char_insert: bool = False,
        content: str = "text",
        **kwargs,
    ):
        """
        初始化方法

        use_sequential_pipeline: 是否启用顺序增强管道#若为 True，则多个增强方法按顺序依次应用，第一个增强方法改完的文本，交给第二个方法继续，以此类推，最终只生成一条叠加效果的数据；否则并行应用，每种增强方法生成各自数据
        num_augmentations: 增强样本数量#[1, 正无穷]#为每条原始文本生成的增强样本数量，数量过大可能导致内存占用过高
        enable_word_delete: 启用单词删除增强#是否启用基于单词随机删除的增强策略
        enable_word_swap: 启用单词交换增强#是否启用基于单词位置交换的增强策略
        enable_word_spelling: 启用拼写错误增强#是否启用引入拼写错误的增强策略
        enable_word_split: 启用单词拆分增强#是否启用将单词拆分为多个子串的增强策略
        enable_char_keyboard: 启用键盘邻键增强#是否启用基于键盘位置扰动的字符级增强策略
        enable_char_ocr: 启用 OCR 错误模拟增强#是否启用模拟 OCR 识别错误的字符级增强策略
        enable_char_delete: 启用字符删除增强#是否启用基于字符随机删除的增强策略
        enable_char_swap: 启用字符交换增强#是否启用基于字符位置交换的增强策略
        enable_char_insert: 启用字符插入增强#是否启用在随机位置插入字符的增强策略
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.num_augmentations = num_augmentations
        self.use_sequential_pipeline = use_sequential_pipeline
        self.content = content

        if self.num_augmentations >= 10:
            logger.warning(
                f"Augmenting with {self.num_augmentations} samples may use significant memory."
            )

        self.aug_pipeline = []

        # Word-level augmenters
        if enable_word_delete:
            self.aug_pipeline.append(naw.RandomWordAug(action=Action.DELETE, aug_p=0.3))
        if enable_word_swap:
            self.aug_pipeline.append(naw.RandomWordAug(action=Action.SWAP, aug_p=0.3))
        if enable_word_spelling:
            self.aug_pipeline.append(naw.SpellingAug())
        if enable_word_split:
            self.aug_pipeline.append(naw.SplitAug())

        # Char-level augmenters
        if enable_char_keyboard:
            self.aug_pipeline.append(nac.KeyboardAug())
        if enable_char_ocr:
            self.aug_pipeline.append(nac.OcrAug())
        if enable_char_delete:
            self.aug_pipeline.append(nac.RandomCharAug(action=Action.DELETE))
        if enable_char_swap:
            self.aug_pipeline.append(nac.RandomCharAug(action=Action.SWAP))
        if enable_char_insert:
            self.aug_pipeline.append(nac.RandomCharAug(action=Action.INSERT))

        if self.use_sequential_pipeline and self.aug_pipeline:
            self.pipeline = naf.Sequential(self.aug_pipeline)
        else:
            self.pipeline = self.aug_pipeline

    def process(self, data: dict) -> list:
        """
        Process a single data sample and return augmented results.

        :param data: dict with at least a text_key field.
        :return: list of dicts with augmented versions of the text.
        """
        text = data[self.content]
        if not self.pipeline:
            return [data]

        aug_texts = []

        if self.use_sequential_pipeline:
            aug_texts = self.pipeline.augment(text, n=self.num_augmentations)
        else:
            for aug in self.pipeline:
                results = aug.augment(text, n=self.num_augmentations)
                aug_texts += results
                # aug_texts += results[1:] if len(results) > 1 else results

        results = []
        for t in aug_texts:
            new_data = deepcopy(data)
            new_data[self.content] = t
            results.append(new_data)

        return results
