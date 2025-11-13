import os, sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from data_engine.processors.nlp.nlp_filter_calculate_loss_single import (
    NlpFilterCalculateLossSingle,
)

from data_engine.utils.transform import sort_and_compare, print_info
from data_engine.utils.test import test_case_list

root_dir = os.path.dirname(os.path.dirname(__file__))
case_list = [
    {
        "class": NlpFilterCalculateLossSingle,
        "params": {
            "model_config": dict(
                model_source="/share/project/hdl/models/Qwen2-7B-Instruct",
                # engine_kwargs=dict(
                #     enable_prefix_caching=True,
                #     enable_chunked_prefill=True,
                #     max_num_batched_tokens=4096,
                # ),
                concurrency=1,
                batch_size=64,
                num_gpus=1,
            )
        },
        "input": [
            {
                "id": "12dc01c2962c20516a9b33a104b51bdb",
                "dataset": "belle_multiturn_chat",
                "content": [
                    {"content": "写一篇关于气候变化的文章。", "role": "user"},
                    {
                        "content": "好的，下面是一篇关于气候变化的文章：\n随着人类活动的不断增加，气候变化已经成为了全球面临的最严重问题之一。这种变化包括了更高的温度，更严重的自然灾害以及更大规模的环境污染等问题。尽管气候变化本身是一项自然现象，但是人类不合理的活动加剧了这一现象。\n事实上，今天的全球变暖与过去变暖不同，它是人类活动的直接结果。科学家在过去的几十年中一直在警告我们，而现在，这种警告变得越来越紧迫。我们必须采取紧急措施，减少人类活动带来的影响，以保护我们的星球。\n然而，减少人类活动带来的影响并不是一项简单的任务。我们需要从经济、社会和环境三个方面出发，寻找可持续的解决方案。这意味着我们需要开展广泛的研究，制定重要的政策、推广创新技术。例如，我们可以通过使用可再生能源、实行节能措施、推广高效的交通方式等方面来减少我们对化石燃料的依赖。\n尽管我们在应对气候变化方面面临着许多困难和不确定性，但是现在不采取行动，将无法避免将来更严重的后果。我们需要采取切实可行的措施，以确保我们的星球能够继续为我们的子孙后代提供一个健康和安全的生活环境。",
                        "role": "assistant",
                    },
                    {"content": "摘要一下这篇文章。", "role": "user"},
                    {
                        "content": "这篇文章讨论了气候变化对人类生存的威胁，人类活动使得气候变暖变得更加严重。文章呼吁我们采取紧急措施来保护地球，必须从经济、社会和环境三个方面出发，寻找可持续的解决方案。",
                        "role": "assistant",
                    },
                ],
                "tags": [
                    "文章写作能力",
                    "摘要总结能力",
                    "气候变化知识",
                    "环境保护意识",
                ],
                "tags_norm": ["闲聊能力", "头脑风暴", "环境保护意识", "文章写作能力"],
                "tags_label": [],
                "calculate_tags": 4,
                "mtld": 2.0632911392,
                "entropy": 6.6189931859,
                "loss": 1.8308104818,
                "tsne_x": -43.0906944275,
                "tsne_y": 28.078458786,
                "sort_key": 1.9910531162,
                "data_leak": False,
                "evol": [
                    {
                        "content": "system\r\n请撰写一篇详细且全面的关于气候变化影响及其应对措施",
                        "role": "user",
                    },
                    {
                        "content": "header\n气候变化的影响及其应对措施：一个全面的分析",
                        "role": "assistant",
                    },
                ],
                "retain": False,
            }
        ],
        "output": [{"text": "我愛北京天安門"}],
        "compare": print_info,
    }
]

if __name__ == "__main__":
    test_case_list(case_list)
