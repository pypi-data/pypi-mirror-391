import os
import ast
import re
from loguru import logger
from typing import Any, Dict, List
import os, sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from data_engine.utils.transform import sort_and_compare, camel_to_snake
from data_engine.utils.transform import extract_class_paths
from data_engine.define import ExecutorType
from data_engine.utils.doc import ray_tool, task_exec_params, actor_exec_params

file_path = os.path.join(root_dir, "data_engine/processors/register.py")
op_set = set()
typ_list = list(ExecutorType)

for type in typ_list:
    op_dict = extract_class_paths(file_path, type)
    op_set |= {i[1] for i in op_dict.values()}


def extract_docstring(node):
    return ast.get_docstring(node) or ""


def parse_class_description(docstring: str):
    lines = [line.strip() for line in docstring.strip().splitlines() if line.strip()]
    label = lines[0] if lines else ""
    label = label.strip(" :-_")
    description = "\n".join(lines[1:] if len(lines) > 1 else [])
    return {"label": label, "description": description}


import re

llm_config = [
    [
        [
            "NlpFilterCalculateLossSingle",
            "NlpFilterDetectKnowledgeDeficiency",
            "NlpFilterEvolFilter",
            "NlpFilterInstructionTags",
            "NlpFilterPerplexity",
            "NlpFilterTokenNum",
            "NlpMapperBiasPatternExplaination",
            "NlpMapperDetectKnowledgeEdge",
            "NlpMapperGenerateSyntheticData",
            "NlpMapperInstanceInferer",
            "NlpMapperInstructionEvol",
        ],
        [
            "Qwen2.5-7B-Instruct",
            "Qwen3-0.6B",
            "Llama-3.2-3B-Instruct",
            "Qwen2.5-1.5B-Instruct",
            "Qwen2.5-32B",
            "Qwen2.5-3B-Instruct",
            "Qwen3-14B",
            "Qwen2.5-14B",
            "Qwen2.5-32B-Instruct",
            "Qwen2.5-72B-Instruct",
            "Llama-3.1-8B-Instruct",
            "Qwen3-32B",
            "Qwen2-7B",
            "Qwen2.5-0.5B",
            "Qwen2.5-14B-Instruct",
            "Qwen2.5-3B",
        ],
    ],
    [
        [
            "VideoMapperClipSeqJointAnnotation",
            "VideoMapperClipSeqSingleAnnotation",
            "VideoMapperMainObjectDetection",
        ],
        [
            "Qwen2-VL-72B-Instruct",
            "Qwen2-VL-7B-Instruct",
        ],
    ],
    [
        ["NlpFilterTagsNorm", "NlpFilterSemanticMapping", "NlpFilterDataLeak"],
        ["all-MiniLM-L6-v2"],
    ],
]


def parse_param_docstring(docstring: str):
    """
    提取 __init__ 中的参数说明，格式为:
    name: 中文名#[可选值1, 可选值2]#描述
    """
    param_info = {}
    lines = [line.strip() for line in docstring.strip().splitlines() if ":" in line]
    for line in lines:
        match = re.match(
            r"^(\w+)\s*:\s*([^\#\[]+?)\s*(?:#\s*\[([^\]]+)\])?\s*#\s*(.*)$", line
        )
        if match:
            name = match.group(1).strip()
            label = match.group(2).strip()
            range_str = match.group(3)
            description = match.group(4).strip()
            info = {"name": name, "label": label, "description": description}
            if range_str:
                info["choice"] = [s.strip(" '\"") for s in range_str.split(",")]
            param_info[name] = info
    return param_info


def extract_init_params(init_node: ast.FunctionDef):
    params = {}
    args = init_node.args.args[1:]  # skip self
    defaults = init_node.args.defaults
    default_offset = len(args) - len(defaults)

    for i, arg in enumerate(args):
        param_name = arg.arg

        # 解析类型注解
        annotation = None
        if arg.annotation is not None:
            try:
                annotation = ast.unparse(arg.annotation)
                annotation = annotation.lower()
            except Exception:
                annotation = None

        # 解析默认值
        default = "无"
        if i >= default_offset:
            try:
                default = ast.literal_eval(defaults[i - default_offset])

            except Exception:
                try:
                    default = ast.unparse(defaults[i - default_offset])
                except Exception:
                    default = "无"

        params[param_name] = {"type": annotation, "default": default}

    return params


def extract_structured_info_from_class_code(code: str):
    tree = ast.parse(code)
    results = []
    for node in tree.body:
        use_class = False
        if isinstance(node, ast.ClassDef) and node.name in op_set:
            # if node.name in ("NlpFilterDataDiversity",):

            if node.name in ray_tool:
                result = ray_tool[node.name]
                if "exec_params" not in result:
                    result["exec_params"] = []
            else:
                class_doc = extract_docstring(node)
                result = {}
                r_dict = parse_class_description(class_doc)
                result.update(r_dict)

                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if (
                                isinstance(target, ast.Name)
                                and target.id == "use_class"
                            ):
                                value = ast.literal_eval(item.value)
                                use_class = value
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        init_doc = extract_docstring(item)
                        param_docs = parse_param_docstring(init_doc)
                        param_defaults = extract_init_params(item)

                        # 合并参数
                        final_params = []
                        for name, meta in param_docs.items():
                            if name in param_defaults:
                                meta["default"] = param_defaults[name]["default"]
                                meta["type"] = param_defaults[name]["type"]
                            final_params.append(meta)
                        result["params"] = final_params
                        result["name"] = camel_to_snake(node.name)
                        result["class_name"] = node.name
                        break
                result["exec_params"] = task_exec_params
                if use_class:
                    result["exec_params"] = actor_exec_params
                    result["use_class"] = True
            if (
                not result["label"]
                or not result.get("name")
                or "S3" in result["class_name"]
                # or "Video" in result["class_name"]
                # or "Audio" in result["class_name"]
                # or "Image" in result["class_name"]
            ):
                # print(node.name)
                pass
            else:
                a = result.get("params") or []
                b = result.get("exec_params") or []
                for p in a + b:
                    if p["name"] == "model_name_or_path":
                        for cc in llm_config:
                            if node.name in cc[0]:
                                p["default"] = cc[1][0]
                                p["choice"] = cc[1]
                                p["type"] = "enum"
                    p["choice"] = p.get("choice") or None
                    if p.get("default") == "无" or "default" not in p:
                        p["require"] = 1
                    else:
                        p["require"] = 0
                    if p["type"] and isinstance(p["type"], str):
                        if p["type"] != "dataSource":
                            p["type"] = p["type"].lower().strip()
                        if p["type"] == "list[str]":
                            p["type"] = "list"
                            p["item_type"] = "str"
                        elif p["type"] == "list[bool]":
                            p["type"] = "list"
                            p["item_type"] = "bool"
                        elif p["type"] == "list[int]":
                            p["type"] = "list"
                            p["item_type"] = "int"
                        elif p["type"] == "list[float]":
                            p["type"] = "list"
                            p["item_type"] = "float"
                        elif p["type"] == "list[Any]":
                            p["type"] = "list"
                            p["item_type"] = ""
                        elif p["type"].startswith("dict["):
                            item_t = p["type"][4:]
                            stripped = item_t.strip()[1:-1]
                            p["item_type"] = [
                                item.strip() for item in stripped.split(",")
                            ]
                            p["type"] = "dict"

                    if p.get("choice"):
                        if p.get("type") == "str":
                            p["type"] = "enum"
                        elif p.get("type") == "float":
                            choices = p.get("choice")
                            p["range"] = {
                                "min": float(choices[0]),
                                "max": float(choices[1]),
                            }
                            p["choice"] = None
                        elif p.get("type") == "int":
                            choices = p.get("choice")
                            if choices[1] == "正无穷":
                                p["range"] = {
                                    "min": int(choices[0]),
                                }
                            p["choice"] = None

                if "Tool" in result["class_name"]:
                    result["category"] = "tool"
                elif "Filter" in result["class_name"]:
                    result["category"] = "filter"
                    names = [i["name"] for i in result["params"]]
                    if "do_filter" not in names:
                        result["params"].insert(
                            0,
                            {
                                "name": "do_filter",
                                "label": "是否过滤数据",
                                "description": "是否过滤数据，为False只打标签，不过滤数据",
                                "default": True,
                                "type": "bool",
                                "choice": None,
                                "require": 0,
                            },
                        )
                elif "Mapper" in result["class_name"]:
                    result["category"] = "mapper"
                elif "Reader" in result["class_name"]:
                    result["category"] = "reader"
                elif "Writer" in result["class_name"]:
                    result["category"] = "consumer"

                results.append(result)
    # results = [i["name"] for i in results]
    new_results = []
    for i in results:
        # if i["name"] in ["ray_writer_jsonline","ray_writer_csv","ray_writer_parquet","tool_limit","tool_count",
        #                  "tool_repartition","tool_take","tool_rename_columns","tool_select_columns","tool_drop_columns","tool_max",
        #                  "tool_min","tool_mean","tool_std","tool_sum","tool_columns","tool_unique","tool_sort","tool_random_sample",
        #                  "tool_add_column","tool_add_id","ray_reader_jsonline","ray_reader_parquet","ray_reader_text","ray_reader_from_items",
        #                  "nlp_filter_action","nlp_filter_alphanumeric","nlp_filter_avg_line_length","nlp_filter_compressibility_ratio",
        #                  "nlp_filter_entity_count","nlp_filter_entity_dependency","nlp_filter_language_score_filter","nlp_filter_paragraph_count",
        #                  "nlp_filter_words_count","nlp_mapper_chinese_text_augment","nlp_mapper_english_text_augment","nlp_mapper_max_line_length",
        #                  "nlp_mapper_remove_non_chinese_characters","nlp_filter_token_num","nlp_filter_stop_words","nlp_mapper_fix_unicode","nlp_mapper_chinese_convert",
        #                  "nlp_filter_flagged_words","nlp_mapper_process_ip_address","nlp_mapper_process_id_card","nlp_mapper_process_mobile_phone",
        #                  "nlp_mapper_process_telephone","nlp_mapper_process_email","nlp_mapper_process_url","tool_md5","tool_take", "python_code",
        #                  "spark_reader","spark_writer", "spark_ollect", "spark_from_items", "spark_take", "spark_count", "tool_rel_to_abs",
        #                  "video_mapper_split_by_scene", "video_filter_motion_score", "video_filter_ocr_ratio", "video_mapper_get_image", "tool_abs_to_rel",
        #                  "tool_nfs_meta", "tool_nfs_file_size", "tool_nfs_delete", "tool_nfs_copy", "nlp_mapper_industry_classification"]:
        # if i["name"] not in ("nlp_mapper_biased_instance_detector", "nlp_mapper_instance_inferer", "nlp_filter_typical_biases_discovery",
        #                      "nlp_mapper_bias_pattern_explaination", "image_mapper_segment", "image_filter_tagging", "image_mapper_captioning_from_gpt4v", "video_filter_motion_score",
        #                      "video_filter_aesthetics", "video_filter_ocr_motion", "video_mapper_clip_seq_get_frames", "video_filter_tagging_from_frames", "video_mapper_get_image",
        #                      "video_mapper_get_clip", "video_mapper_get_frames", "image_text_filter_similarity", "tool_nfs_delete", "tool_extract_pdf", "nlp_mapper_instruction_evol",
        #                      "nlp_filter_proportion_adjust", "image_filter_watermark","image_mapper_shape", "image_filter_shape",
        #                      ):
        if i["name"] not in (
            "nlp_mapper_biased_instance_detector",
            "nlp_mapper_instance_inferer",
            "nlp_filter_typical_biases_discovery",
            "nlp_mapper_bias_pattern_explaination",
            "image_mapper_segment",
            "image_filter_tagging",
            "image_mapper_captioning_from_gpt4v",
            "video_filter_aesthetics",
            "video_filter_ocr_motion",
            "video_mapper_clip_seq_get_frames",
            "video_filter_tagging_from_frames",
            "video_mapper_get_clip",
            "video_mapper_get_frames",
            "image_text_filter_similarity",
            "nlp_filter_proportion_adjust",
            "image_filter_watermark",
            "image_mapper_shape",
            "image_filter_shape",
        ):
            new_results.append(i)
    return new_results


def extract_from_directory(root_path: str) -> List[Dict[str, Any]]:
    extracted_data = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        rr = extract_structured_info_from_class_code(code)

                        for r in rr:
                            if r.get("use_class"):
                                r["description"] += "\n当前算子需要GPU"
                            if (
                                "ray" in file_path
                                or "only_ray = True" in code
                                or r.get("use_class")
                            ):
                                r.pop("use_class", None)
                                r["engine"] = ["ray"]
                            elif "spark" in file_path:
                                r["engine"] = ["spark"]
                            else:
                                r["engine"] = ["spark", "ray"]
                            extracted_data.append(r)
                except Exception as e:
                    logger.exception(e)
                    print(f"跳过文件 {file_path}，因读取/解析错误: {e}")
    # extracted_data = [{"name": i["label"],"class": i["class_name"],} for i in extracted_data]
    # print({i["name"] for i in extracted_data})
    # extracted_data = [{"name": i["name"], "params": i["params"]} for i in extracted_data]
    return extracted_data


if __name__ == "__main__":
    result = extract_from_directory(os.path.join(root_dir, "data_engine/processors/"))
    import json

    print(f"op count {len(result)}")
    with open("result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"gen doc success")
