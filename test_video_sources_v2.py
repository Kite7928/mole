#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频源延迟和稳定性测试脚本 V2
"""
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import json
import re

# 从JSON配置提取的视频源
VIDEO_SOURCES = {
    "czzy55.com": {
        "name": "[厂长]",
        "api": "https://www.czzy55.com/api.php/provide/vod",
        "detail": "https://www.czzy55.com/"
    },
    "yqkan.com": {
        "name": "[一起看]",
        "api": "https://yqkan.com/api.php/provide/vod",
        "detail": "https://yqkan.com"
    },
    "nangua.com": {
        "name": "[南瓜]",
        "api": "https://api.nangua.cc/api.php/provide/vod",
        "detail": "https://nangua.cc"
    },
    "kkys.com": {
        "name": "[酷看]",
        "api": "https://kkys.me/api.php/provide/vod",
        "detail": "https://kkys.me"
    },
    "appld.com": {
        "name": "[率率]",
        "api": "https://api.appld.com/api.php/provide/vod",
        "detail": "https://appld.com"
    },
    "appmao.com": {
        "name": "[萌米]",
        "api": "https://api.appmao.com/api.php/provide/vod",
        "detail": "https://appmao.com"
    },
    "rinhome.com": {
        "name": "[荐片]",
        "api": "http://api2.rinhome.com/api.php/provide/vod",
        "detail": "http://api2.rinhome.com"
    },
    "ddrk.com": {
        "name": "[低端]",
        "api": "https://ddrk.me/api.php/provide/vod",
        "detail": "https://ddrk.me"
    },
    "auete.pro": {
        "name": "[奥特]",
        "api": "https://auete.pro/api.php/provide/vod",
        "detail": "https://auete.pro/"
    },
    "maolvys.com": {
        "name": "[毛驴]",
        "api": "https://www.maolvys.com/api.php/provide/vod",
        "detail": "https://www.maolvys.com/"
    },
    "hdmyy.com": {
        "name": "[新视觉]",
        "api": "https://www.hdmyy.com/api.php/provide/vod",
        "detail": "https://www.hdmyy.com/"
    },
    "bttwoo.com": {
        "name": "[比特]",
        "api": "https://bttwoo.com/api.php/provide/vod",
        "detail": "https://bttwoo.com"
    },
    "libvio.pw": {
        "name": "[LibVio]",
        "api": "https://www.libvio.pw/api.php/provide/vod",
        "detail": "https://www.libvio.pw/"
    },
    "kuaikan.com": {
        "name": "[快看]",
        "api": "https://kuaikan.com/api.php/provide/vod",
        "detail": "https://kuaikan.com"
    },
    "kunyu77.com": {
        "name": "[酷云七七]",
        "api": "https://api.kunyu77.com/api.php/provide/vod",
        "detail": "https://kunyu77.com"
    },
    "sp33.com": {
        "name": "[360]",
        "api": "https://www.sp33.com/api.php/provide/vod",
        "detail": "https://www.sp33.com"
    },
    "xb6v.com": {
        "name": "[新6V]",
        "api": "http://www.xb6v.com/api.php/provide/vod",
        "detail": "http://www.xb6v.com/"
    },
    "anime1.com": {
        "name": "[动漫]",
        "api": "https://anime1.me/api.php/provide/vod",
        "detail": "https://anime1.me"
    },
    "dm84.com": {
        "name": "[动漫巴士]",
        "api": "https://dm84.com/api.php/provide/vod",
        "detail": "https://dm84.com"
    },
    "ysj.com": {
        "name": "[异世界]",
        "api": "https://ysj.vip/api.php/provide/vod",
        "detail": "https://ysj.vip"
    },
    "aiduanju.vip": {
        "name": "[短剧]",
        "api": "http://aiduanju.vip/api.php/provide/vod",
        "detail": "http://aiduanju.vip/"
    },
    "yj1211.com": {
        "name": "[在线直播]",
        "api": "https://api.yj1211.work/api.php/provide/vod",
        "detail": "https://yj1211.work"
    },
    "kanqiu.com": {
        "name": "[88看球]",
        "api": "https://kanqiu.com/api.php/provide/vod",
        "detail": "https://kanqiu.com"
    },
    "wogg.xyz": {
        "name": "[玩偶哥哥]",
        "api": "https://www.wogg.xyz/api.php/provide/vod",
        "detail": "https://www.wogg.xyz"
    },
    "yiso.fun": {
        "name": "[易搜]",
        "api": "https://yiso.fun/api.php/provide/vod",
        "detail": "https://yiso.fun"
    },
    "pansou.vip": {
        "name": "[盘搜]",
        "api": "https://pansou.vip/api.php/provide/vod",
        "detail": "https://pansou.vip"
    },
    "upyunso.com": {
        "name": "[UP云搜]",
        "api": "https://upyunso.com/api.php/provide/vod",
        "detail": "https://upyunso.com"
    },
    "pansearch.me": {
        "name": "[盘搜索]",
        "api": "https://pansearch.me/api.php/provide/vod",
        "detail": "https://pansearch.me"
    },
    "dovx.cc": {
        "name": "[七夜]",
        "api": "https://dovx.cc/api.php/provide/vod",
        "detail": "https://dovx.cc"
    },
    "zhaozy.com": {
        "name": "[找资源]",
        "api": "https://zhaozy.com/api.php/provide/vod",
        "detail": "https://zhaozy.com"
    }
}

# 测试参数
TEST_ROUNDS = 10  # 每个源测试10次，更准确
TIMEOUT = 10  # 超时时间(秒)


def test_source(domain: str, source_info: Dict, rounds: int = TEST_ROUNDS) -> Dict:
    """
    测试单个视频源的延迟和稳定性

    Args:
        domain: 域名
        source_info: 源信息
        rounds: 测试轮数

    Returns:
        测试结果字典
    """
    name = source_info["name"]
    api_url = source_info["api"]
    latencies = []
    success_count = 0
    status_codes = []

    print(f"\n测试 {name} ({domain})...")

    for i in range(rounds):
        try:
            start_time = time.time()
            response = requests.get(
                api_url,
                params={"ac": "list"},  # 获取列表
                timeout=TIMEOUT
            )
            end_time = time.time()

            latency = (end_time - start_time) * 1000  # 转换为毫秒
            latencies.append(latency)
            success_count += 1
            status_codes.append(response.status_code)

            print(f"  轮次 {i+1}/{rounds}: {latency:.2f}ms, 状态码: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"  轮次 {i+1}/{rounds}: 超时")
            status_codes.append(None)
        except requests.exceptions.ConnectionError:
            print(f"  轮次 {i+1}/{rounds}: 连接错误")
            status_codes.append(None)
        except Exception as e:
            print(f"  轮次 {i+1}/{rounds}: 错误 - {str(e)}")
            status_codes.append(None)

    # 计算统计信息
    success_rate = (success_count / rounds) * 100 if rounds > 0 else 0

    if latencies:
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        std_deviation = statistics.stdev(latencies) if len(latencies) > 1 else 0
    else:
        avg_latency = float('inf')
        min_latency = float('inf')
        max_latency = float('inf')
        std_deviation = 0

    return {
        "domain": domain,
        "name": name,
        "api": api_url,
        "detail": source_info["detail"],
        "success_rate": success_rate,
        "avg_latency": avg_latency,
        "min_latency": min_latency,
        "max_latency": max_latency,
        "std_deviation": std_deviation,
        "success_count": success_count,
        "total_tests": rounds,
        "status_codes": status_codes
    }


def test_all_sources(sources: Dict, max_workers: int = 3) -> List[Dict]:
    """
    并发测试所有视频源

    Args:
        sources: 视频源字典
        max_workers: 最大并发数

    Returns:
        测试结果列表
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(test_source, domain, info): domain
            for domain, info in sources.items()
        }

        for future in as_completed(futures):
            domain = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"\n[X] 测试 {domain} 时发生错误: {str(e)}")

    return results


def print_results(results: List[Dict]):
    """打印测试结果"""
    print("\n" + "="*100)
    print("测试结果汇总")
    print("="*100)

    # 按成功率降序、平均延迟升序排序
    sorted_results = sorted(
        results,
        key=lambda x: (-x["success_rate"], x["avg_latency"])
    )

    print(f"\n{'排名':<6}{'源名称':<20}{'成功率':<12}{'平均延迟':<12}{'最小延迟':<12}{'最大延迟':<12}{'稳定性':<12}")
    print("-"*100)

    for idx, result in enumerate(sorted_results, 1):
        if result["avg_latency"] == float('inf'):
            avg_str = "N/A"
            min_str = "N/A"
            max_str = "N/A"
            stability_str = "N/A"
        else:
            avg_str = f"{result['avg_latency']:.2f}ms"
            min_str = f"{result['min_latency']:.2f}ms"
            max_str = f"{result['max_latency']:.2f}ms"
            stability_str = f"{result['std_deviation']:.2f}ms"

        print(f"{idx:<6}{result['name']:<20}{result['success_rate']:<12.1f}%{avg_str:<12}{min_str:<12}{max_str:<12}{stability_str:<12}")

    return sorted_results


def select_top_sources(results: List[Dict], top_n: int = 8) -> List[Dict]:
    """
    选择最优的N个源

    选择标准:
    1. 成功率 >= 80%
    2. 按成功率降序
    3. 按平均延迟升序
    4. 按稳定性(标准差)升序

    Args:
        results: 测试结果列表
        top_n: 选择数量

    Returns:
        最优源列表
    """
    # 过滤成功率 >= 80% 的源
    filtered = [r for r in results if r["success_rate"] >= 80]

    # 排序: 成功率降序 -> 平均延迟升序 -> 稳定性升序
    sorted_filtered = sorted(
        filtered,
        key=lambda x: (-x["success_rate"], x["avg_latency"], x["std_deviation"])
    )

    # 选择前N个
    top_sources = sorted_filtered[:top_n]

    print("\n" + "="*100)
    print(f"推荐的 {top_n} 个最优视频源")
    print("="*100)

    for idx, source in enumerate(top_sources, 1):
        print(f"\n{idx}. {source['name']} ({source['domain']})")
        print(f"   API: {source['api']}")
        print(f"   成功率: {source['success_rate']:.1f}%")
        if source['avg_latency'] != float('inf'):
            print(f"   平均延迟: {source['avg_latency']:.2f}ms")
            print(f"   延迟范围: {source['min_latency']:.2f}ms - {source['max_latency']:.2f}ms")
            print(f"   稳定性(标准差): {source['std_deviation']:.2f}ms")

    return top_sources


def save_results(results: List[Dict], top_sources: List[Dict]):
    """保存结果到JSON文件"""
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "all_results": results,
        "top_8_sources": top_sources
    }

    with open("video_source_test_results_v2.json", "w", encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 测试结果已保存到 video_source_test_results_v2.json")


def main():
    """主函数"""
    print("="*100)
    print("视频源延迟和稳定性测试 V2")
    print(f"测试源数量: {len(VIDEO_SOURCES)}")
    print(f"每个源测试轮数: {TEST_ROUNDS}")
    print(f"超时时间: {TIMEOUT}秒")
    print("="*100)

    # 测试所有源
    results = test_all_sources(VIDEO_SOURCES)

    # 打印结果
    sorted_results = print_results(results)

    # 选择最优8个
    top_sources = select_top_sources(sorted_results, top_n=8)

    # 保存结果
    save_results(results, top_sources)

    print("\n" + "="*100)
    print("测试完成!")
    print("="*100)


if __name__ == "__main__":
    main()