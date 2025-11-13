import yaml
import os

root_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

with open(os.path.join(root_dir, "asset/kg_rag/config.yaml"), "r") as f:
    config_data = yaml.safe_load(f)

with open(os.path.join(root_dir, "asset/kg_rag/system_prompts.yaml"), "r") as f:
    system_prompts = yaml.safe_load(f)

if "GPT_CONFIG_FILE" in config_data:
    config_data["GPT_CONFIG_FILE"] = config_data["GPT_CONFIG_FILE"].replace(
        "$HOME", os.environ["HOME"]
    )


__all__ = ["config_data", "system_prompts"]
