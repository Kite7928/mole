#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比两次测试结果并生成最终的最优8个源配置
"""
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import time

# 第一次测试结果 (从之前测试中提取)
FIRST_TEST_RESULTS = [
    {"name": "[猫眼资源]", "domain": "www.maoyanzy.com", "api": "https://api.maoyanapi.top/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 276.24, "std_deviation": 13.70},
    {"name": "[360资源]", "domain": "360zy.com", "api": "https://360zyzz.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 772.45, "std_deviation": 48.50},
    {"name": "[天涯影视]", "domain": "tyyszy.com", "api": "https://tyyszy.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1008.38, "std_deviation": 199.11},
    {"name": "[卧龙资源]", "domain": "wolongzyw.com", "api": "https://wolongzyw.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1019.10, "std_deviation": 16.37},
    {"name": "[旺旺资源]", "domain": "api.wwzy.tv", "api": "https://api.wwzy.tv/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1183.20, "std_deviation": 337.29},
    {"name": "[暴风资源]", "domain": "bfzy.tv", "api": "https://bfzyapi.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1211.11, "std_deviation": 569.11},
    {"name": "[金鹰点播]", "domain": "jinyingzy.com", "api": "https://jinyingzy.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1531.78, "std_deviation": 873.53},
    {"name": "[百度云zy]", "domain": "bdzy1.com", "api": "https://pz.168188.dpdns.org/?url=https://api.apibdzy.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 1532.68, "std_deviation": 1026.58}
]

# 第二次测试结果 (从V2测试中提取)
SECOND_TEST_RESULTS = [
    {"name": "[快看]", "domain": "kuaikan.com", "api": "https://kuaikan.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 211.41, "std_deviation": 75.13},
    {"name": "[易搜]", "domain": "yiso.fun", "api": "https://yiso.fun/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 226.36, "std_deviation": 15.68},
    {"name": "[找资源]", "domain": "zhaozy.com", "api": "https://zhaozy.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 283.64, "std_deviation": 115.40},
    {"name": "[比特]", "domain": "bttwoo.com", "api": "https://bttwoo.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 508.84, "std_deviation": 229.29},
    {"name": "[酷看]", "domain": "kkys.me", "api": "https://kkys.me/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 717.67, "std_deviation": 189.62},
    {"name": "[动漫]", "domain": "anime1.com", "api": "https://anime1.me/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 901.38, "std_deviation": 327.19},
    {"name": "[厂长]", "domain": "czzy55.com", "api": "https://www.czzy55.com/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 2440.51, "std_deviation": 1691.89},
    {"name": "[玩偶哥哥]", "domain": "wogg.xyz", "api": "https://www.wogg.xyz/api.php/provide/vod", "success_rate": 100.0, "avg_latency": 2482.29, "std_deviation": 1455.98}
]


def compare_and_merge():
    """
    对比两次测试结果,选择最优的8个源

    选择标准:
    1. 成功率 >= 80%
    2. 按平均延迟升序
    3. 按稳定性(标准差)升序
    """
    print("="*100)
    print("对比两次测试结果")
    print("="*100)

    # 合并所有结果
    all_sources = FIRST_TEST_RESULTS + SECOND_TEST_RESULTS

    # 去重 (如果有重复的域名，保留延迟更低的)
    unique_sources = {}
    for source in all_sources:
        domain = source["domain"]
        if domain not in unique_sources:
            unique_sources[domain] = source
        else:
            # 如果已存在，选择延迟更低的
            if source["avg_latency"] < unique_sources[domain]["avg_latency"]:
                unique_sources[domain] = source

    # 转换为列表
    final_sources = list(unique_sources.values())

    # 排序: 成功率降序 -> 平均延迟升序 -> 稳定性升序
    final_sources.sort(
        key=lambda x: (-x["success_rate"], x["avg_latency"], x["std_deviation"])
    )

    # 选择前8个
    top_8 = final_sources[:8]

    print("\n最终推荐的8个最优视频源")
    print("="*100)

    for idx, source in enumerate(top_8, 1):
        print(f"\n{idx}. {source['name']} ({source['domain']})")
        print(f"   API: {source['api']}")
        print(f"   成功率: {source['success_rate']:.1f}%")
        print(f"   平均延迟: {source['avg_latency']:.2f}ms")
        print(f"   稳定性(标准差): {source['std_deviation']:.2f}ms")

    # 生成JSON配置
    config = {
        "cache_time": 7200,
        "api_site": {}
    }

    for source in top_8:
        config["api_site"][source["domain"]] = {
            "name": source["name"],
            "api": source["api"],
            "detail": source["api"].replace("/api.php/provide/vod", "")
        }

    # 保存配置
    with open("final_top_8_sources.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    print("\n" + "="*100)
    print("最终配置已保存到 final_top_8_sources.json")
    print("="*100)

    # 打印配置预览
    print("\n配置预览:")
    print(json.dumps(config, ensure_ascii=False, indent=4))

    return top_8


def main():
    """主函数"""
    print("\n第一次测试结果 (5轮测试):")
    print(f"测试源数量: {len(FIRST_TEST_RESULTS)}")
    for source in FIRST_TEST_RESULTS:
        print(f"  {source['name']}: {source['avg_latency']:.2f}ms, 稳定性: {source['std_deviation']:.2f}ms")

    print("\n第二次测试结果 (10轮测试):")
    print(f"测试源数量: {len(SECOND_TEST_RESULTS)}")
    for source in SECOND_TEST_RESULTS:
        print(f"  {source['name']}: {source['avg_latency']:.2f}ms, 稳定性: {source['std_deviation']:.2f}ms")

    top_8 = compare_and_merge()

    print("\n" + "="*100)
    print("对比完成!")
    print("="*100)


if __name__ == "__main__":
    main()