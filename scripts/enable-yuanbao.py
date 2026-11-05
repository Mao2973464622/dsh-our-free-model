#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""启用元宝反代（yuanbao）渠道。

前置条件：必须先部署并运行 yuanbao-openai-api
          https://github.com/Mao2973464622/yuanbao-openai-api
          默认监听 http://127.0.0.1:8788

本脚本只把 yuanbao 写进数据目录 settings.json 的
aggregate.providers 并置 enabled=true。
（registry.json 中已有 provider 定义，无需重复添加。）

用法：
    python3 scripts/enable-yuanbao.py
    python3 scripts/enable-yuanbao.py --port 9000
    python3 scripts/enable-yuanbao.py --data-dir /path/to/ofm-home
    python3 scripts/enable-yuanbao.py --enable-search
"""
import argparse
import json
import os

MODELS = [
    "deepseek",
    "deepseek-v3",
    "deep_seek_v3",
    "hy3",
    "hunyuan",
    "hunyuan-t1",
    "hunyuan_gpt_175B_0404",
    "hy4",
    "hunyuan_omnipotent_hy4",
]

SEARCH_MODELS = [
    "deepseek-search",
    "deepseek-v3-search",
    "deep_seek_v3-search",
    "hy3-search",
    "hunyuan-search",
    "hunyuan-t1-search",
    "hunyuan_gpt_175B_0404-search",
    "hy4-search",
    "hunyuan_omnipotent_hy4-search",
]


def resolve_data_dir(explicit):
    if explicit:
        return os.path.expanduser(explicit)
    if os.environ.get("OFM_HOME"):
        return os.path.expanduser(os.environ["OFM_HOME"])
    return os.path.expanduser("~/.our-free-model")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8788, help="yuanbao-openai-api 监听端口，默认 8788")
    ap.add_argument("--host", default="127.0.0.1", help="yuanbao-openai-api 主机，默认 127.0.0.1")
    ap.add_argument("--data-dir", default=None, help="本项目数据目录（含 settings.json）")
    ap.add_argument("--enable-search", action="store_true", help="同时启用 -search 联网变体")
    args = ap.parse_args()

    data_dir = resolve_data_dir(args.data_dir)
    settings_path = os.path.join(data_dir, "settings.json")

    if os.path.exists(settings_path):
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
    else:
        os.makedirs(data_dir, exist_ok=True)
        settings = {}
        print(f"[init] 未找到 settings.json，将在 {settings_path} 新建")

    base_url = f"http://{args.host}:{args.port}/v1"

    aggregate = settings.setdefault("aggregate", {})
    aggregate["enabled"] = True
    providers = aggregate.setdefault("providers", {})

    models = list(MODELS)
    if args.enable_search:
        models += SEARCH_MODELS

    entry = providers.setdefault("yuanbao", {})
    entry["enabled"] = True
    entry["baseUrl"] = base_url
    entry["apiKey"] = entry.get("apiKey") or "sk-local-yuanbao"
    entry["models"] = models

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"[ok] 已写入 {settings_path}")
    print(f"     baseUrl : {base_url}")
    print(f"     models  : {len(models)} 个")
    print()
    print("下一步：重启本项目服务，然后调用 yuanbao/<模型名>")
    print("自检：curl -s " + base_url + "/models")


if __name__ == "__main__":
    main()