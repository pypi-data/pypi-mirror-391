#!/usr/bin/env python3
"""
视频处理器的单元测试
"""
import os, sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from data_engine.processors.nlp.nlp_mapper_chinese_convert import (
    NlpMapperChineseConvert,
)
from data_engine.processors.nlp.nlp_mapper_clean_html import CleanHtmlMapper
from data_engine.processors.nlp.nlp_mapper_chinese_text_augment import (
    NlpMapperChineseTextAugment,
)
from data_engine.processors.nlp.nlp_mapper_english_text_augment import (
    NlpMapperEnglishTextAugment,
)
from data_engine.processors.nlp.nlp_filter_action import NlpFilterAction
from data_engine.processors.nlp.nlp_filter_compressibility_ratio import (
    NlpFilterCompressibilityRatio,
)
from data_engine.processors.nlp.nlp_filter_entity_count import NlpFilterEntityCount
from data_engine.processors.nlp.nlp_filter_entity_dependency import (
    NlpFilterEntityDependency,
)
from data_engine.processors.nlp.nlp_filter_flagged_words import NlpFilterFlaggedWords
from data_engine.processors.nlp.nlp_filter_industry_classification import (
    NlpMapperIndustryClassification,
)
from data_engine.processors.nlp.nlp_filter_max_line_length import NlpMapperMaxLineLength
from data_engine.processors.nlp.nlp_filter_perplexity import NlpFilterPerplexity
from data_engine.processors.nlp.nlp_filter_stopwords import NlpFilterStopWords
from data_engine.processors.nlp.nlp_filter_token_num import NlpFilterTokenNum
from data_engine.processors.nlp.nlp_mapper_delete_non_chinese_character import (
    NlpMapperRemoveNonChineseCharacters,
)
from data_engine.processors.nlp.nlp_mapper_fix_unicode import NlpMapperFixUnicode
from data_engine.processors.nlp.nlp_mapper_whitespace_normalization import (
    NlpMapperWhitespaceNormalizer,
)
from data_engine.processors.nlp.nlp_filter_quality_score import NlpFilterQualityScore
from data_engine.processors.nlp.nlp_filter_avg_line_length import NlpFilterAvgLineLength
from data_engine.processors.nlp.nlp_filter_language_score import (
    NlpFilterLanguageScoreFilter,
)
from data_engine.processors.nlp.nlp_filter_alphanumeric import NlpFilterAlphanumeric
from data_engine.processors.nlp.nlp_filter_words_count import NlpFilterWordsCount
from data_engine.processors.nlp.nlp_filter_paragraph_count import (
    NlpFilterParagraphCount,
)

from data_engine.utils.transform import sort_and_compare, print_info
from data_engine.utils.test import test_case_list, test_case_list_spark

root_dir = os.path.dirname(os.path.dirname(__file__))
case_list = [
    {
        "class": NlpMapperChineseConvert,
        "params": {"mode": "s2tw"},
        "input": [{"text": "我爱北京天安门"}],
        "output": [{"text": "我愛北京天安門"}],
        "compare": sort_and_compare,
    },
    {
        "class": CleanHtmlMapper,
        "params": {"mode": "s2tw"},
        "input": [{"text": "<li>我爱北京天安门<li>"}],
        "output": [{"text": "*我爱北京天安门\n*"}],
        "compare": sort_and_compare,
    },
    {
        "class": NlpMapperChineseTextAugment,
        "params": {
            "aug_num": 2,
            "sequential": False,
            "keep_original_sample": True,
            "replace_similar_word": True,
            "replace_homophone_char": True,
            "delete_random_char": True,
            "swap_random_char": False,
            "replace_equivalent_num": True,
        },
        "input": [{"text": "这里一共有5种不同的数据增强方法"}],
        "output": [
            {"text": "此间一共有5种不同的数据增强方法"},
            {"text": "这里一共有5种不同的多寡增强方法"},
            {"text": "这里一共有5种不同的数踽增强纺法"},
            {"text": "这里一共有5种不同的数据增樯方法"},
            {"text": "这里一共有5种不同的数据增强"},
            {"text": "这里一共有5种不同数据增强"},
            {"text": "这里一共有伍种不同的数据增强方法"},
            {"text": "这里①共有5种不同的数据增强方法"},
        ],
        "compare": print_info,
    },
    {
        "class": NlpMapperEnglishTextAugment,
        "params": {
            "enable_char_keyboard": True,
            "enable_char_delete": True,
            "num_augmentations": 2,
            "include_original": False,
        },
        "input": [{"text": "This is a simple test sentence."}],
        "output": [
            {"text": "fuis is a wimpl2 test sFHtDnce."},
            {"text": "is is a smpl et sentence."},
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterAction,
        "params": {},
        "input": [{"text": "我爱北京天安门"}],
        "output": [{"text": "我爱北京天安门", "num_action": 1}],
        "compare": print_info,
    },
    {
        "class": NlpFilterAction,
        "params": {
            "lang": "en",
        },
        "input": [{"text": "This is a simple test sentence."}],
        "output": [{"text": "This is a simple test sentence.", "num_action": 0}],
        "compare": print_info,
    },
    {
        "class": NlpFilterCompressibilityRatio,
        "params": {},
        "input": [{"text": "This is a simple test sentence."}],
        "output": [
            {
                "text": "This is a simple test sentence.",
                "compression_ratio": 1.5806451612903225,
            }
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterEntityCount,
        "params": {},
        "input": [{"text": "This is a simple test sentence."}],
        "output": [
            {
                "text": "This is a simple test sentence.",
                "compression_ratio": 1.5806451612903225,
            }
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterEntityDependency,
        "params": {},
        "input": [{"text": "This is a simple test sentence."}],
        "output": [
            {
                "text": "This is a simple test sentence.",
                "compression_ratio": 1.5806451612903225,
            }
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterFlaggedWords,
        "params": {"sensitive_words": ["暴力", "仇恨", "攻击"]},
        "input": [{"text": "他充满了仇恨和攻击性"}],
        "output": [
            {"text": "他充满了仇恨和攻击性", "sensitive_ratio": 0.16666666666666666}
        ],
        "compare": print_info,
    },
    {
        "class": NlpMapperIndustryClassification,
        "params": {"model_name_or_path": "classification"},
        "input": [{"text": "他充满了仇恨和攻击性"}],
        "output": [
            {"text": "他充满了仇恨和攻击性", "sensitive_ratio": 0.16666666666666666}
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterQualityScore,
        "params": {"model_name_or_path": "quality_score"},
        "input": [{"text": "他充满了仇恨和攻击性"}],
        "output": [
            {"text": "他充满了仇恨和攻击性", "sensitive_ratio": 0.16666666666666666}
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterAvgLineLength,
        "params": {},
        "input": [{"text": "他充满了仇恨和攻击性"}],
        "output": [{"text": "他充满了仇恨和攻击性", "avg_line_length": 10.0}],
        "compare": print_info,
    },
    {
        "class": NlpFilterLanguageScoreFilter,
        "params": {},
        "input": [{"text": "他充满了仇恨和攻击性"}],
        "output": [{"text": "他充满了仇恨和攻击性", "avg_line_length": 10.0}],
        "compare": print_info,
    },
    {
        "class": NlpFilterAlphanumeric,
        "params": {},
        "input": [{"text": "他充满了仇恨和攻击性1231"}],
        "output": [{"text": "他充满了仇恨和攻击性1231", "alnum_ratio": 1.0}],
        "compare": print_info,
    },
    {
        "class": NlpFilterWordsCount,
        "params": {},
        "input": [{"text": "他充满了仇恨和攻击性1231"}],
        "output": [{"text": "他充满了仇恨和攻击性1231", "words_count": 7}],
        "compare": print_info,
    },
    {
        "class": NlpFilterParagraphCount,
        "params": {},
        "input": [{"text": "这是第一段。\n\n这是第二段。\n   \n这是第三段。"}],
        "output": [
            {
                "text": "这是第一段。\n\n这是第二段。\n   \n这是第三段。",
                "paragraphs_count": 3,
            }
        ],
        "compare": print_info,
    },
    {
        "class": NlpMapperMaxLineLength,
        "params": {},
        "input": [{"text": "他充满了仇恨和攻击性\n他充斥着仇恨和攻击性"}],
        "output": [
            {"text": "他充满了仇恨和攻击性", "sensitive_ratio": 0.16666666666666666}
        ],
        "compare": print_info,
    },
    {
        "class": NlpFilterPerplexity,
        "params": {
            "model_name_or_path": "Qwen2.5-0.5B",
            "exec_params": {"num_gpus": 1},
        },
        "input": [{"text": "<li>我爱北京天安门<li>"}],
        "output": [{"text": "<li>我爱北京天安门<li>", "perplexity": 76.74076843261719}],
        "compare": print_info,
    },
    {
        "class": NlpFilterStopWords,
        "params": {"stopwords_list": ["的", "了", "在", "and", "is", "to"]},
        "input": [{"text": "我在学校学习编程，这是非常有趣的事情。"}],
        "output": [{"text": "<li>我爱北京天安门<li>", "perplexity": 76.74076843261719}],
        "compare": print_info,
    },
    {
        "class": NlpFilterTokenNum,
        "params": {
            "stopwords_list": ["的", "了", "在", "and", "is", "to"],
            "model_name_or_path": "Qwen2.5-0.5B",
        },
        "input": [{"text": "我在学校学习编程，这是非常有趣的事情。"}],
        "output": [{"text": "<li>我爱北京天安门<li>", "perplexity": 76.74076843261719}],
        "compare": print_info,
    },
    {
        "class": NlpMapperRemoveNonChineseCharacters,
        "params": {
            "keep_alphabet": False,
            "keep_number": False,
        },
        "input": [{"text": "你好，Hello! 123。@#￥%……&*（）"}],
        "output": [{"text": "<li>我爱北京天安门<li>", "perplexity": 76.74076843261719}],
        "compare": print_info,
    },
    {
        "class": NlpMapperFixUnicode,
        "params": {},
        "input": [
            {"text": "这是一段中文\u3000\u3000中间有奇怪的空格和\uff08全角括号\uff09。"}
        ],
        "output": [{"text": "这是一段中文  中间有奇怪的空格和(全角括号)。"}],
        "compare": print_info,
    },
    {
        "class": NlpMapperWhitespaceNormalizer,
        "params": {},
        "input": [
            {"text": "你好\u3000世界\u00a0！\u2003这是\u2009一个\u2028测试\u2029。"}
        ],
        "output": [{"text": "你好 世界 ！ 这是 一个 测试 。"}],
        "compare": print_info,
    },
]


if __name__ == "__main__":
    # test_case_list(case_list)
    test_case_list_spark(case_list)
