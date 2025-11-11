#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from loguru import logger
import os, contextlib

with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    import nlpcda
from data_engine.core.base import BaseMapper


class NlpMapperChineseTextAugment(BaseMapper):
    """
    中文文本增强映射器

    该类基于 nlpcda 库实现对单条中文文本样本的增强处理，支持多种增强方法的选择和组合。
    通过配置参数，控制增强样本的数量、增强方式（顺序或并行）、以及是否保留原始样本等。
    """

    def __init__(
        self,
        sequential: bool = False,
        aug_num: int = 1,
        keep_original_sample: bool = True,
        replace_similar_word: bool = False,
        replace_homophone_char: bool = False,
        delete_random_char: bool = False,
        swap_random_char: bool = False,
        replace_equivalent_num: bool = False,
        content: str = "text",
        **kwargs,
    ):
        """
        初始化方法
        sequential: 是否顺序增强#是否按顺序依次应用各增强方法，最终只生成一条叠加效果的数据，若为 False，则并行应用各增强方法，每种增强方法生成各自数据
        aug_num: 增强样本数量#每个增强方法生成的增强样本数量
        # keep_original_sample: 保留原始样本#是否在返回结果中包含原始输入样本（该参数在当前实现中未使用）
        replace_similar_word: 替换相似词#是否启用相似词替换增强
        replace_homophone_char: 替换同音字#是否启用同音字替换增强
        delete_random_char: 随机删除字符#是否启用随机删除字符增强
        swap_random_char: 随机交换字符#是否启用随机交换字符增强
        replace_equivalent_num: 替换等价数字#是否启用等价数字替换增强
        content: 文本#数据中待识别文本的字段名称
        """
        super().__init__(**kwargs)
        self.aug_num = aug_num
        self.sequential = sequential
        self.content = content

        if aug_num >= 10:
            logger.warning(
                f"Augmenting with {aug_num} samples may use significant memory."
            )

        self.aug_pipeline = []

        def _create_num():
            return (
                (self.aug_num + 1)
                if not self.sequential or len(self.aug_pipeline) == 0
                else 2
            )

        if replace_similar_word:
            self.aug_pipeline.append(nlpcda.Similarword(create_num=_create_num()))
        if replace_homophone_char:
            self.aug_pipeline.append(nlpcda.Homophone(create_num=_create_num()))
        if delete_random_char:
            self.aug_pipeline.append(nlpcda.RandomDeleteChar(create_num=_create_num()))
        if swap_random_char:
            self.aug_pipeline.append(
                nlpcda.CharPositionExchange(create_num=_create_num(), char_gram=1)
            )
        if replace_equivalent_num:
            self.aug_pipeline.append(nlpcda.EquivalentChar(create_num=_create_num()))

    def process(self, data: dict) -> list:
        """
        Process a single data and return augmented results.

        :param data: dict with at least a text_key field.
        :return: dict with possibly augmented versions of text_key field.
        """

        aug_texts = []

        if len(self.aug_pipeline) == 0:
            return [data]
        text = data[self.content]
        if self.sequential:
            texts = [text]
            for aug in self.aug_pipeline:
                results = []
                for t in texts:
                    r = aug.replace(t)
                    results += r[1:] if len(r) > 1 else r
                texts = results[:]
            aug_texts = texts
        else:
            for aug in self.aug_pipeline:
                aug_texts += aug.replace(text)[1:]
        # return [{**data, "text": i} for i in aug_texts]
        return [{**data, self.content: i} for i in aug_texts]
