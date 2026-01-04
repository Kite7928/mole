#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频源延迟和稳定性测试脚本 V3
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

# 从新JSON配置提取的视频源
VIDEO_SOURCES = {
    "api.1080zyku.com": {
        "name": "[TV-1080资源]",
        "api": "https://api.1080zyku.com/inc/api_mac10.php",
        "detail": "https://api.1080zyku.com"
    },
    "155api.com": {
        "name": "[AV-155资源]",
        "api": "https://155api.com/api.php/provide/vod",
        "detail": "https://155api.com"
    },
    "360zy.com": {
        "name": "[TV-360资源]",
        "api": "https://360zy.com/api.php/provide/vod",
        "detail": "https://360zy.com"
    },
    "ckzy.me": {
        "name": "[TV-CK资源]",
        "api": "https://ckzy.me/api.php/provide/vod",
        "detail": "https://ckzy.me"
    },
    "api.ukuapi.com": {
        "name": "[TV-U酷资源1]",
        "api": "https://api.ukuapi.com/api.php/provide/vod",
        "detail": "https://api.ukuapi.com"
    },
    "api.ukuapi88.com": {
        "name": "[TV-U酷资源2]",
        "api": "https://api.ukuapi88.com/api.php/provide/vod",
        "detail": "https://api.ukuapi88.com"
    },
    "ikunzyapi.com": {
        "name": "[TV-ikun资源]",
        "api": "https://ikunzyapi.com/api.php/provide/vod",
        "detail": "https://ikunzyapi.com"
    },
    "api.wujinapi.cc": {
        "name": "[TV-wujinapi无尽]",
        "api": "https://api.wujinapi.cc/api.php/provide/vod",
        "detail": ""
    },
    "cj.yayazy.net": {
        "name": "[TV-丫丫点播]",
        "api": "https://cj.yayazy.net/api.php/provide/vod",
        "detail": "https://cj.yayazy.net"
    },
    "api.guangsuapi.com": {
        "name": "[TV-光速资源]",
        "api": "https://api.guangsuapi.com/api.php/provide/vod",
        "detail": "https://api.guangsuapi.com"
    },
    "collect.wolongzyw.com": {
        "name": "[TV-卧龙点播]",
        "api": "https://collect.wolongzyw.com/api.php/provide/vod",
        "detail": "https://collect.wolongzyw.com"
    },
    "collect.wolongzy.cc": {
        "name": "[TV-卧龙资源2]",
        "api": "https://collect.wolongzy.cc/api.php/provide/vod",
        "detail": ""
    },
    "wolongzyw.com": {
        "name": "[TV-卧龙资源]",
        "api": "https://wolongzyw.com/api.php/provide/vod",
        "detail": "https://wolongzyw.com"
    },
    "tyyszy.com": {
        "name": "[TV-天涯资源]",
        "api": "https://tyyszy.com/api.php/provide/vod",
        "detail": "https://tyyszy.com"
    },
    "cj.rycjapi.com": {
        "name": "[TV-如意资源]",
        "api": "https://cj.rycjapi.com/api.php/provide/vod",
        "detail": ""
    },
    "zy.xmm.hk": {
        "name": "[TV-小猫咪资源]",
        "api": "https://zy.xmm.hk/api.php/provide/vod",
        "detail": "https://zy.xmm.hk"
    },
    "api.xinlangapi.com": {
        "name": "[TV-新浪点播]",
        "api": "https://api.xinlangapi.com/xinlangapi.php/provide/vod",
        "detail": "https://api.xinlangapi.com"
    },
    "api.wujinapi.com": {
        "name": "[TV-无尽资源1]",
        "api": "https://api.wujinapi.com/api.php/provide/vod",
        "detail": ""
    },
    "api.wujinapi.me": {
        "name": "[TV-无尽资源2]",
        "api": "https://api.wujinapi.me/api.php/provide/vod",
        "detail": ""
    },
    "api.wujinapi.net": {
        "name": "[TV-无尽资源3]",
        "api": "https://api.wujinapi.net/api.php/provide/vod",
        "detail": ""
    },
    "wwzy.tv": {
        "name": "[TV-旺旺短剧]",
        "api": "https://wwzy.tv/api.php/provide/vod",
        "detail": "https://wwzy.tv"
    },
    "api.wwzy.tv": {
        "name": "[TV-旺旺资源]",
        "api": "https://api.wwzy.tv/api.php/provide/vod",
        "detail": "https://api.wwzy.tv"
    },
    "bfzyapi.com": {
        "name": "[TV-暴风资源]",
        "api": "https://bfzyapi.com/api.php/provide/vod",
        "detail": ""
    },
    "zuidazy.me": {
        "name": "[TV-最大点播]",
        "api": "http://zuidazy.me/api.php/provide/vod",
        "detail": "http://zuidazy.me"
    },
    "api.zuidapi.com": {
        "name": "[TV-最大资源]",
        "api": "https://api.zuidapi.com/api.php/provide/vod",
        "detail": "https://api.zuidapi.com"
    },
    "m3u8.apiyhzy.com": {
        "name": "[TV-樱花资源]",
        "api": "https://m3u8.apiyhzy.com/api.php/provide/vod",
        "detail": ""
    },
    "api.yparse.com": {
        "name": "[TV-步步高资源]",
        "api": "https://api.yparse.com/api/json",
        "detail": ""
    },
    "api.niuniuzy.me": {
        "name": "[TV-牛牛点播]",
        "api": "https://api.niuniuzy.me/api.php/provide/vod",
        "detail": "https://api.niuniuzy.me"
    },
    "caiji.dyttzyapi.com": {
        "name": "[TV-电影天堂资源]",
        "api": "http://caiji.dyttzyapi.com/api.php/provide/vod",
        "detail": "http://caiji.dyttzyapi.com"
    },
    "api.bwzyz.com": {
        "name": "[AV-百万资源]",
        "api": "https://api.bwzyz.com/api.php/provide/vod",
        "detail": "https://api.bwzyz.com"
    },
    "api.apibdzy.com": {
        "name": "[TV-百度云资源]",
        "api": "https://api.apibdzy.com/api.php/provide/vod",
        "detail": "https://api.apibdzy.com"
    },
    "suoniapi.com": {
        "name": "[TV-索尼资源]",
        "api": "https://suoniapi.com/api.php/provide/vod",
        "detail": ""
    },
    "www.hongniuzy2.com": {
        "name": "[TV-红牛资源]",
        "api": "https://www.hongniuzy2.com/api.php/provide/vod",
        "detail": "https://www.hongniuzy2.com"
    },
    "caiji.maotaizy.cc": {
        "name": "[TV-茅台资源]",
        "api": "https://caiji.maotaizy.cc/api.php/provide/vod",
        "detail": "https://caiji.maotaizy.cc"
    },
    "www.huyaapi.com": {
        "name": "[TV-虎牙资源]",
        "api": "https://www.huyaapi.com/api.php/provide/vod",
        "detail": "https://www.huyaapi.com"
    },
    "caiji.dbzy.tv": {
        "name": "[TV-豆瓣资源1]",
        "api": "https://caiji.dbzy.tv/api.php/provide/vod",
        "detail": "https://caiji.dbzy.tv"
    },
    "dbzy.tv": {
        "name": "[TV-豆瓣资源2]",
        "api": "https://dbzy.tv/api.php/provide/vod",
        "detail": "https://dbzy.tv"
    },
    "hhzyapi.com": {
        "name": "[TV-豪华资源]",
        "api": "https://hhzyapi.com/api.php/provide/vod",
        "detail": "https://hhzyapi.com"
    },
    "subocaiji.com": {
        "name": "[TV-速博资源]",
        "api": "https://subocaiji.com/api.php/provide/vod",
        "detail": ""
    },
    "cj.lziapi.com": {
        "name": "[TV-量子资源]",
        "api": "https://cj.lziapi.com/api.php/provide/vod",
        "detail": ""
    },
    "jinyingzy.com": {
        "name": "[TV-金鹰点播]",
        "api": "https://jinyingzy.com/api.php/provide/vod",
        "detail": "https://jinyingzy.com"
    },
    "jyzyapi.com": {
        "name": "[TV-金鹰资源]",
        "api": "https://jyzyapi.com/api.php/provide/vod",
        "detail": "https://jyzyapi.com"
    },
    "sdzyapi.com": {
        "name": "[TV-閃電资源]",
        "api": "https://sdzyapi.com/api.php/provide/vod",
        "detail": "https://sdzyapi.com"
    },
    "cj.ffzyapi.com": {
        "name": "[TV-非凡资源]",
        "api": "https://cj.ffzyapi.com/api.php/provide/vod",
        "detail": "https://cj.ffzyapi.com"
    },
    "p2100.net": {
        "name": "[TV-飘零资源]",
        "api": "https://p2100.net/api.php/provide/vod",
        "detail": "https://p2100.net"
    },
    "mozhuazy.com": {
        "name": "[TV-魔爪资源]",
        "api": "https://mozhuazy.com/api.php/provide/vod",
        "detail": "https://mozhuazy.com"
    },
    "caiji.moduapi.cc": {
        "name": "[TV-魔都动漫]",
        "api": "https://caiji.moduapi.cc/api.php/provide/vod",
        "detail": "https://caiji.moduapi.cc"
    },
    "www.mdzyapi.com": {
        "name": "[TV-魔都资源]",
        "api": "https://www.mdzyapi.com/api.php/provide/vod",
        "detail": "https://www.mdzyapi.com"
    },
    "json.heimuer.xyz": {
        "name": "[TV-黑木耳]",
        "api": "https://json.heimuer.xyz/api.php/provide/vod",
        "detail": "https://json.heimuer.xyz"
    },
    "json02.heimuer.xyz": {
        "name": "[TV-黑木耳点播]",
        "api": "https://json02.heimuer.xyz/api.php/provide/vod",
        "detail": "https://json02.heimuer.xyz"
    },
    "api.fczy888.me": {
        "name": "[蜂巢片库]",
        "api": "https://api.fczy888.me/api.php/provide/vod",
        "detail": ""
    },
    "api.jmzy.com": {
        "name": "[金马资源网]",
        "api": "https://api.jmzy.com/api.php/provide/vod",
        "detail": ""
    },
    "dadiapi.com": {
        "name": "[大地资源网络]",
        "api": "https://dadiapi.com/api.php/provide/vod",
        "detail": ""
    },
    "api.xiaojizy.live": {
        "name": "[小鸡资源]",
        "api": "https://api.xiaojizy.live/provide/vod",
        "detail": ""
    },
    "caiji.kuaichezy.org": {
        "name": "[快车资源]",
        "api": "https://caiji.kuaichezy.org/api.php/provide",
        "detail": ""
    },
    "www.xxibaozyw.com": {
        "name": "[细胞采集]",
        "api": "https://www.xxibaozyw.com/api.php/provide/vod",
        "detail": ""
    },
    "www.qiqidys.com": {
        "name": "[七七影视]",
        "api": "https://www.qiqidys.com/api.php/provide/vod/",
        "detail": ""
    },
    "www.fantuan.tv": {
        "name": "[饭团影视]",
        "api": "https://www.fantuan.tv/api.php/provide/vod/",
        "detail": ""
    }
}

# 测试参数
TEST_ROUNDS = 10  # 每个源测试10次
TIMEOUT = 10  # 超时时间(秒)


def test_source(domain: str, source_info: Dict, rounds: int = TEST_ROUNDS) -> Dict:
    """
    测试单个视频源的延迟和稳定性
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
                params={"ac": "list"},
                timeout=TIMEOUT
            )
            end_time = time.time()

            latency = (end_time - start_time) * 1000
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

    print(f"\n{'排名':<6}{'源名称':<25}{'成功率':<12}{'平均延迟':<12}{'最小延迟':<12}{'最大延迟':<12}{'稳定性':<12}")
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

        print(f"{idx:<6}{result['name']:<25}{result['success_rate']:<12.1f}%{avg_str:<12}{min_str:<12}{max_str:<12}{stability_str:<12}")

    return sorted_results


def select_top_sources(results: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    选择最优的N个源
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
        "top_10_sources": top_sources
    }

    with open("video_source_test_results_v3.json", "w", encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] 测试结果已保存到 video_source_test_results_v3.json")


def main():
    """主函数"""
    print("="*100)
    print("视频源延迟和稳定性测试 V3")
    print(f"测试源数量: {len(VIDEO_SOURCES)}")
    print(f"每个源测试轮数: {TEST_ROUNDS}")
    print(f"超时时间: {TIMEOUT}秒")
    print("="*100)

    # 测试所有源
    results = test_all_sources(VIDEO_SOURCES)

    # 打印结果
    sorted_results = print_results(results)

    # 选择最优10个
    top_sources = select_top_sources(sorted_results, top_n=10)

    # 保存结果
    save_results(results, top_sources)

    print("\n" + "="*100)
    print("测试完成!")
    print("="*100)


if __name__ == "__main__":
    main()