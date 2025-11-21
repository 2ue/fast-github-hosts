#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Hosts 自动生成工具 - Pro版本
功能：DoH查询 + 纯TCP测速 + 智能缓存 + 域名分级
作者：基于Ultra版本深度优化
版本：2.0.0 Pro
"""

import dns.resolver
import subprocess
import socket
import concurrent.futures
import time
import json
import argparse
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sys

# ==================== 配置区 ====================

# 域名分级配置
DOMAIN_LEVELS = {
    'core': [
        # ===== 核心服务（20个）- 必须成功 =====
        'github.com',
        'api.github.com',
        'gist.github.com',
        'codeload.github.com',
        'github.blog',
        'github.community',
        'github.dev',
        'alive.github.com',
        'live.github.com',
        'education.github.com',

        # ===== CDN与静态资源（5个）=====
        'github.githubassets.com',
        'github.io',
        'github.map.fastly.net',
        'github.global.ssl.fastly.net',
        'githubstatus.com',

        # ===== UserContent核心（5个）=====
        'raw.githubusercontent.com',
        'objects.githubusercontent.com',
        'avatars.githubusercontent.com',
        'camo.githubusercontent.com',
        'user-images.githubusercontent.com',
    ],

    'extended': [
        # ===== 更多UserContent（16个）=====
        'raw.github.com',
        'objects-origin.githubusercontent.com',
        'release-assets.githubusercontent.com',
        'github-releases.githubusercontent.com',
        'github-registry-files.githubusercontent.com',
        'avatars0.githubusercontent.com',
        'avatars1.githubusercontent.com',
        'avatars2.githubusercontent.com',
        'avatars3.githubusercontent.com',
        'avatars4.githubusercontent.com',
        'avatars5.githubusercontent.com',
        'private-user-images.githubusercontent.com',
        'cloud.githubusercontent.com',
        'desktop.githubusercontent.com',
        'favicons.githubusercontent.com',
        'media.githubusercontent.com',
        'pkg-containers.githubusercontent.com',

        # ===== 包管理器（13个）=====
        'ghcr.io',
        'maven.pkg.github.com',
        'npm.pkg.github.com',
        'npm-proxy.pkg.github.com',
        'npm-beta.pkg.github.com',
        'npm-beta-proxy.pkg.github.com',
        'nuget.pkg.github.com',
        'rubygems.pkg.github.com',
        'pypi.pkg.github.com',
        'swift.pkg.github.com',
        'docker.pkg.github.com',
        'docker-proxy.pkg.github.com',
        'containers.pkg.github.com',

        # ===== AWS S3存储（5个）=====
        'github-cloud.s3.amazonaws.com',
        'github-com.s3.amazonaws.com',
        'github-production-release-asset-2e65be.s3.amazonaws.com',
        'github-production-user-asset-6210df.s3.amazonaws.com',
        'github-production-repository-file-5c1aeb.s3.amazonaws.com',

        # ===== GitHub Copilot（7个）=====
        'githubcopilot.com',
        'api.githubcopilot.com',
        'api.individual.githubcopilot.com',
        'copilot-proxy.githubusercontent.com',
        'copilot-telemetry.githubusercontent.com',
        'default.exp-tas.com',
        'collector.github.com',
        'central.github.com',
    ],

    'optional': [
        # ===== GitHub Actions核心（9个）=====
        'pipelines.actions.githubusercontent.com',
        'vstoken.actions.githubusercontent.com',
        'broker.actions.githubusercontent.com',
        'launch.actions.githubusercontent.com',
        'runner-auth.actions.githubusercontent.com',
        'tokenghub.actions.githubusercontent.com',
        'setup-tools.actions.githubusercontent.com',
        'pkg.actions.githubusercontent.com',
        'results-receiver.actions.githubusercontent.com',
        'mpsghub.actions.githubusercontent.com',

        # ===== Actions Pipelines（28个）=====
        'pipelinesghubeus1.actions.githubusercontent.com',
        'pipelinesghubeus2.actions.githubusercontent.com',
        'pipelinesghubeus3.actions.githubusercontent.com',
        'pipelinesghubeus4.actions.githubusercontent.com',
        'pipelinesghubeus5.actions.githubusercontent.com',
        'pipelinesghubeus6.actions.githubusercontent.com',
        'pipelinesghubeus7.actions.githubusercontent.com',
        'pipelinesghubeus8.actions.githubusercontent.com',
        'pipelinesghubeus9.actions.githubusercontent.com',
        'pipelinesghubeus10.actions.githubusercontent.com',
        'pipelinesghubeus11.actions.githubusercontent.com',
        'pipelinesghubeus12.actions.githubusercontent.com',
        'pipelinesghubeus13.actions.githubusercontent.com',
        'pipelinesghubeus14.actions.githubusercontent.com',
        'pipelinesghubeus15.actions.githubusercontent.com',
        'pipelinesghubeus20.actions.githubusercontent.com',
        'pipelinesghubeus21.actions.githubusercontent.com',
        'pipelinesghubeus22.actions.githubusercontent.com',
        'pipelinesghubeus23.actions.githubusercontent.com',
        'pipelinesghubeus24.actions.githubusercontent.com',
        'pipelinesghubeus25.actions.githubusercontent.com',
        'pipelinesghubeus26.actions.githubusercontent.com',
        'pipelinesproxcnc1.actions.githubusercontent.com',
        'pipelinesproxcus1.actions.githubusercontent.com',
        'pipelinesproxeau1.actions.githubusercontent.com',
        'pipelinesproxsdc1.actions.githubusercontent.com',
        'pipelinesproxweu1.actions.githubusercontent.com',
        'pipelinesproxwus31.actions.githubusercontent.com',

        # ===== Actions Runners（12个）=====
        'runnerghubeus1.actions.githubusercontent.com',
        'runnerghubeus20.actions.githubusercontent.com',
        'runnerghubeus21.actions.githubusercontent.com',
        'runnerghubwus31.actions.githubusercontent.com',
        'runnerproxcnc1.actions.githubusercontent.com',
        'runnerproxcus1.actions.githubusercontent.com',
        'runnerproxeau1.actions.githubusercontent.com',
        'runnerproxsdc1.actions.githubusercontent.com',
        'runnerproxweu1.actions.githubusercontent.com',
        'run-actions-1-azure-eastus.actions.githubusercontent.com',
        'run-actions-2-azure-eastus.actions.githubusercontent.com',
        'run-actions-3-azure-eastus.actions.githubusercontent.com',

        # ===== Azure Blob存储 - Actions结果（20个）=====
        'productionresultssa0.blob.core.windows.net',
        'productionresultssa1.blob.core.windows.net',
        'productionresultssa2.blob.core.windows.net',
        'productionresultssa3.blob.core.windows.net',
        'productionresultssa4.blob.core.windows.net',
        'productionresultssa5.blob.core.windows.net',
        'productionresultssa6.blob.core.windows.net',
        'productionresultssa7.blob.core.windows.net',
        'productionresultssa8.blob.core.windows.net',
        'productionresultssa9.blob.core.windows.net',
        'productionresultssa10.blob.core.windows.net',
        'productionresultssa11.blob.core.windows.net',
        'productionresultssa12.blob.core.windows.net',
        'productionresultssa13.blob.core.windows.net',
        'productionresultssa14.blob.core.windows.net',
        'productionresultssa15.blob.core.windows.net',
        'productionresultssa16.blob.core.windows.net',
        'productionresultssa17.blob.core.windows.net',
        'productionresultssa18.blob.core.windows.net',
        'productionresultssa19.blob.core.windows.net',

        # ===== Azure Blob存储 - 包管理器（4个）=====
        'mavenregistryv2prod.blob.core.windows.net',
        'npmregistryv2prod.blob.core.windows.net',
        'nugetregistryv2prod.blob.core.windows.net',
        'rubygemsregistryv2prod.blob.core.windows.net',

        # ===== 安全认证（3个）=====
        'tuf-repo.github.com',
        'fulcio.githubapp.com',
        'timestamp.githubapp.com',

        # ===== 开发工具（1个）=====
        'vscode.dev',
    ]
}

# DoH服务器列表（DNS-over-HTTPS）- 2025年最佳实践
DOH_SERVERS = [
    'https://1.1.1.1/dns-query',          # Cloudflare
    'https://8.8.8.8/resolve',             # Google
    'https://223.5.5.5/resolve',           # 阿里DNS（国内）
]

# 传统DNS服务器列表（降级使用）
DNS_SERVERS = [
    '1.1.1.1',          # Cloudflare DNS
    '8.8.8.8',          # Google DNS
    '223.5.5.5',        # 阿里DNS
    '114.114.114.114',  # 114DNS
]

# 测速配置
TCP_TEST_COUNT = 3      # TCP测试次数（取中位数）
TCP_TIMEOUT = 2         # TCP连接超时（秒）
TCP_PORT = 443          # 测试端口
MAX_WORKERS = 10        # 最大并发数
TOP_IP_COUNT = 3        # 返回前N个最快IP

# 缓存配置
CACHE_FILE = '.github_hosts_cache.json'
CACHE_ENABLED = True

# ==================== DoH查询模块 ====================

def query_dns_doh(domain: str, doh_server: str) -> List[str]:
    """
    使用DNS-over-HTTPS查询域名

    Args:
        domain: 域名
        doh_server: DoH服务器地址

    Returns:
        IP地址列表
    """
    try:
        import requests

        params = {
            'name': domain,
            'type': 'A'
        }

        headers = {
            'accept': 'application/dns-json'
        }

        response = requests.get(
            doh_server,
            params=params,
            headers=headers,
            timeout=3
        )

        if response.status_code == 200:
            data = response.json()
            answers = data.get('Answer', [])
            ips = [ans['data'] for ans in answers if ans.get('type') == 1]  # A记录
            return ips

        return []
    except Exception as e:
        # print(f"  ⚠️  DoH查询失败 {domain} @ {doh_server}: {e}")
        return []


def query_dns_doh_all(domain: str) -> List[str]:
    """
    从所有DoH服务器查询并合并结果

    Args:
        domain: 域名

    Returns:
        去重后的IP地址列表
    """
    all_ips = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOH_SERVERS)) as executor:
        futures = [
            executor.submit(query_dns_doh, domain, doh_server)
            for doh_server in DOH_SERVERS
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                ips = future.result()
                all_ips.extend(ips)
            except Exception:
                pass

    return list(set(all_ips))


# ==================== 传统DNS查询模块 ====================

def query_dns_traditional(domain: str, dns_server: str) -> List[str]:
    """
    使用传统DNS服务器查询域名的A记录

    Args:
        domain: 域名
        dns_server: DNS服务器地址

    Returns:
        IP地址列表
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = 3
        resolver.lifetime = 3

        answers = resolver.resolve(domain, 'A')
        return [str(rdata) for rdata in answers]
    except Exception as e:
        # print(f"  ⚠️  DNS查询失败 {domain} @ {dns_server}: {e}")
        return []


def query_dns_traditional_all(domain: str) -> List[str]:
    """
    从多个传统DNS服务器获取IP并去重

    Args:
        domain: 域名

    Returns:
        去重后的IP地址列表
    """
    all_ips = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(DNS_SERVERS)) as executor:
        futures = [
            executor.submit(query_dns_traditional, domain, dns_server)
            for dns_server in DNS_SERVERS
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                ips = future.result()
                all_ips.extend(ips)
            except Exception:
                pass

    # 去重并过滤无效IP
    unique_ips = list(set(all_ips))
    valid_ips = [
        ip for ip in unique_ips
        if not ip.startswith('127.')
        and not ip.startswith('0.')
        and not ip.startswith('169.254.')  # 过滤APIPA地址
    ]

    return valid_ips


# ==================== 三层降级DNS查询 ====================

def get_all_ips(domain: str, use_doh: bool = True) -> List[str]:
    """
    三层降级策略获取域名IP：DoH → 传统DNS → Web爬虫

    Args:
        domain: 域名
        use_doh: 是否使用DoH

    Returns:
        IP地址列表
    """
    # Layer 1: DoH查询（最优，防DNS污染）
    if use_doh:
        try:
            ips = query_dns_doh_all(domain)
            if ips:
                return ips
        except Exception:
            pass

    # Layer 2: 传统DNS查询（降级）
    try:
        ips = query_dns_traditional_all(domain)
        if ips:
            return ips
    except Exception:
        pass

    # Layer 3: Web爬虫（最后手段，暂不实现）
    # 可以在这里添加 ipaddress.com 爬虫逻辑

    return []


# ==================== 纯TCP测速模块 ====================

def test_tcp_speed(ip: str, port: int = TCP_PORT, timeout: int = TCP_TIMEOUT) -> float:
    """
    测试TCP连接速度（毫秒）

    Args:
        ip: IP地址
        port: 端口号
        timeout: 超时时间

    Returns:
        连接耗时（毫秒），失败返回inf
    """
    try:
        start_time = time.time()
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        elapsed_ms = (time.time() - start_time) * 1000
        return elapsed_ms
    except Exception:
        return float('inf')


def test_tcp_latency(ip: str, count: int = TCP_TEST_COUNT) -> float:
    """
    多次TCP测试取中位数（比平均值更稳定）

    Args:
        ip: IP地址
        count: 测试次数

    Returns:
        中位数延迟（毫秒），失败返回inf
    """
    results = []

    for _ in range(count):
        latency = test_tcp_speed(ip, TCP_PORT, TCP_TIMEOUT)
        if latency != float('inf'):
            results.append(latency)

    if not results:
        return float('inf')

    # 排序后取中位数
    results.sort()
    mid = len(results) // 2

    if len(results) % 2 == 0:
        # 偶数个结果，取中间两个的平均值
        return (results[mid - 1] + results[mid]) / 2
    else:
        # 奇数个结果，直接取中间值
        return results[mid]


# ==================== 智能缓存模块 ====================

def load_cache() -> Dict:
    """加载缓存的IP和成功率"""
    if not CACHE_ENABLED or not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache: Dict):
    """保存缓存"""
    if not CACHE_ENABLED:
        return

    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def update_cache(domain: str, ip: str, latency: float):
    """更新IP成功记录（滑动平均）"""
    if not CACHE_ENABLED:
        return

    cache = load_cache()
    key = f"{domain}:{ip}"

    if key not in cache:
        cache[key] = {
            'count': 0,
            'avg_latency': 0,
            'last_success': None
        }

    # 滑动平均
    old_avg = cache[key]['avg_latency']
    count = cache[key]['count']
    cache[key]['avg_latency'] = (old_avg * count + latency) / (count + 1)
    cache[key]['count'] += 1
    cache[key]['last_success'] = datetime.now().isoformat()

    save_cache(cache)


def get_cached_ips(domain: str) -> List[Tuple[str, float]]:
    """获取缓存中的IP及其历史延迟"""
    cache = load_cache()
    results = []

    for key, data in cache.items():
        if key.startswith(f"{domain}:"):
            ip = key.split(':', 1)[1]
            results.append((ip, data['avg_latency']))

    return results


# ==================== 核心处理模块 ====================

def get_fastest_ips(domain: str, use_doh: bool = True, use_cache: bool = True) -> List[Tuple[str, float]]:
    """
    获取域名的最快前N个IP

    Args:
        domain: 域名
        use_doh: 是否使用DoH
        use_cache: 是否使用缓存

    Returns:
        [(IP, 延迟)] 列表，按延迟排序
    """
    print(f"🔍 正在处理: {domain}")

    # 1. 获取所有IP
    ips = get_all_ips(domain, use_doh)

    # 如果启用缓存，添加历史成功的IP
    if use_cache:
        cached_ips = get_cached_ips(domain)
        cached_ip_list = [ip for ip, _ in cached_ips]
        ips = list(set(ips + cached_ip_list))

    if not ips:
        print(f"  ❌ 未找到IP")
        return []

    print(f"  📡 找到 {len(ips)} 个IP: {', '.join(ips[:3])}{'...' if len(ips) > 3 else ''}")

    # 2. 并发测速
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(ips), 5)) as executor:
        future_to_ip = {
            executor.submit(test_tcp_latency, ip, TCP_TEST_COUNT): ip
            for ip in ips
        }

        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                latency = future.result()
                results[ip] = latency

                if latency != float('inf'):
                    print(f"  ⚡ {ip}: {latency:.2f}ms")
                    # 更新缓存
                    update_cache(domain, ip, latency)
            except Exception:
                results[ip] = float('inf')

    # 3. 选择最快的N个IP
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    valid_results = [(ip, latency) for ip, latency in sorted_results if latency != float('inf')]

    if valid_results:
        top_n = valid_results[:TOP_IP_COUNT]
        print(f"  ✅ 最快IP: {', '.join([f'{ip}({lat:.2f}ms)' for ip, lat in top_n])}")
        return top_n
    else:
        # 所有IP都测速失败，返回第一个
        if ips:
            print(f"  ⚠️  所有IP测速失败，使用默认: {ips[0]}")
            return [(ips[0], float('inf'))]
        return []


# ==================== 文件生成模块 ====================

def get_domain_list(level: str) -> List[str]:
    """
    根据级别获取域名列表

    Args:
        level: 'core', 'extended', 'full'

    Returns:
        域名列表
    """
    if level == 'core':
        return DOMAIN_LEVELS['core']
    elif level == 'extended':
        return DOMAIN_LEVELS['core'] + DOMAIN_LEVELS['extended']
    elif level == 'full':
        return DOMAIN_LEVELS['core'] + DOMAIN_LEVELS['extended'] + DOMAIN_LEVELS['optional']
    else:
        return DOMAIN_LEVELS['core']


def generate_hosts_file(
    output_file: str = 'github_hosts_pro',
    level: str = 'extended',
    use_doh: bool = True,
    use_cache: bool = True,
    multi_ip: bool = True
):
    """
    生成hosts文件

    Args:
        output_file: 输出文件路径
        level: 域名级别 (core/extended/full)
        use_doh: 是否使用DoH
        use_cache: 是否使用缓存
        multi_ip: 是否使用多IP轮询
    """
    domains = get_domain_list(level)

    print("=" * 70)
    print("🚀 GitHub Hosts 自动生成工具 - Pro版本 v2.0.0")
    print("=" * 70)
    print(f"📋 域名级别: {level.upper()}")
    print(f"📋 域名总数: {len(domains)}")
    print(f"🌐 DNS方式: {'DoH (DNS-over-HTTPS)' if use_doh else '传统DNS'}")
    print(f"⚡ 测速方法: 纯TCP中位数 ({TCP_TEST_COUNT}次)")
    print(f"💾 智能缓存: {'启用' if use_cache else '禁用'}")
    print(f"🔄 多IP轮询: {'启用' if multi_ip else '禁用'}")
    print("=" * 70)
    print()

    # 开始时间
    start_time = time.time()

    # 并发处理所有域名
    results = {}
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_domain = {
            executor.submit(get_fastest_ips, domain, use_doh, use_cache): domain
            for domain in domains
        }

        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                ip_list = future.result()
                if ip_list:
                    results[domain] = ip_list
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理失败: {domain} - {e}")

    # 生成hosts文件内容
    hosts_content = []
    hosts_content.append("# GitHub Hosts Pro - 企业级解决方案")
    hosts_content.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    hosts_content.append(f"# 域名级别: {level.upper()}")
    hosts_content.append(f"# 域名总数: {success_count}/{len(domains)}")
    hosts_content.append(f"# DNS方式: {'DoH (防污染)' if use_doh else '传统DNS'}")
    hosts_content.append(f"# 测速方法: 纯TCP中位数")
    hosts_content.append(f"# 多IP轮询: {'启用 (前{TOP_IP_COUNT}个最快IP)' if multi_ip else '禁用'}")
    hosts_content.append("#")
    hosts_content.append("# ==================== GitHub Hosts Start ====================")
    hosts_content.append("")

    # 按域名排序输出
    for domain in domains:
        if domain in results:
            ip_list = results[domain]

            if multi_ip:
                # 多IP模式：写入前N个最快IP
                for ip, latency in ip_list:
                    latency_str = f"# {latency:.2f}ms" if latency != float('inf') else "# timeout"
                    hosts_content.append(f"{ip:<20} {domain:<50} {latency_str}")
            else:
                # 单IP模式：只写入最快的一个
                ip, latency = ip_list[0]
                latency_str = f"# {latency:.2f}ms" if latency != float('inf') else "# timeout"
                hosts_content.append(f"{ip:<20} {domain:<50} {latency_str}")

    hosts_content.append("")
    hosts_content.append("# ==================== GitHub Hosts End ====================")
    hosts_content.append("")

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(hosts_content))

    # 统计信息
    elapsed_time = time.time() - start_time

    print()
    print("=" * 70)
    print(f"✅ Hosts文件已生成: {output_file}")
    print(f"✅ 成功获取: {success_count}/{len(domains)} 个域名")
    print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
    if use_cache:
        print(f"💾 缓存文件: {CACHE_FILE}")
    print("=" * 70)
    print()
    print("📝 使用方法:")
    print("  Linux/Mac: sudo cat github_hosts_pro >> /etc/hosts")
    print("  Windows:   追加到 C:\\Windows\\System32\\drivers\\etc\\hosts")
    print()
    print("🔄 刷新DNS:")
    print("  Linux:   sudo systemd-resolve --flush-caches")
    print("  Mac:     sudo killall -HUP mDNSResponder")
    print("  Windows: ipconfig /flushdns")
    print()
    print("💡 提示:")
    print(f"  - 快速模式: python {sys.argv[0]} --level=core")
    print(f"  - 标准模式: python {sys.argv[0]} --level=extended (默认)")
    print(f"  - 完整模式: python {sys.argv[0]} --level=full")
    print(f"  - 禁用缓存: python {sys.argv[0]} --no-cache")
    print(f"  - 单IP模式: python {sys.argv[0]} --no-multi-ip")
    print()


# ==================== 主程序 ====================

if __name__ == '__main__':
    try:
        # 命令行参数解析
        parser = argparse.ArgumentParser(
            description='GitHub Hosts 自动生成工具 - Pro版本',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  快速模式（20个核心域名）:
    python %(prog)s --level=core

  标准模式（65个域名）:
    python %(prog)s --level=extended

  完整模式（141个域名）:
    python %(prog)s --level=full

  禁用DoH（使用传统DNS）:
    python %(prog)s --no-doh

  禁用缓存:
    python %(prog)s --no-cache

  单IP模式:
    python %(prog)s --no-multi-ip
            """
        )

        parser.add_argument(
            '--level',
            choices=['core', 'extended', 'full'],
            default='extended',
            help='域名级别: core(20个), extended(65个), full(141个) [默认: extended]'
        )

        parser.add_argument(
            '--output',
            default='github_hosts_pro',
            help='输出文件路径 [默认: github_hosts_pro]'
        )

        parser.add_argument(
            '--no-doh',
            action='store_true',
            help='禁用DoH，使用传统DNS查询'
        )

        parser.add_argument(
            '--no-cache',
            action='store_true',
            help='禁用智能缓存'
        )

        parser.add_argument(
            '--no-multi-ip',
            action='store_true',
            help='禁用多IP轮询，只使用最快的一个IP'
        )

        args = parser.parse_args()

        # 检查依赖
        try:
            import dns.resolver
        except ImportError:
            print("❌ 缺少依赖: dnspython")
            print("📦 请安装: pip install dnspython")
            sys.exit(1)

        try:
            import requests
        except ImportError:
            print("❌ 缺少依赖: requests")
            print("📦 请安装: pip install requests")
            sys.exit(1)

        # 生成hosts文件
        generate_hosts_file(
            output_file=args.output,
            level=args.level,
            use_doh=not args.no_doh,
            use_cache=not args.no_cache,
            multi_ip=not args.no_multi_ip
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
