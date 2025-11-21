#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Hosts 自动生成工具 - Ultimate版本
功能：DoH查询 + 纯TCP测速 + 智能缓存 + 域名分级 + Daemon模式 + HTTP API + 统计报告
作者：基于Pro版本终极优化
版本：3.0.0 Ultimate
"""

import dns.resolver
import socket
import concurrent.futures
import time
import json
import argparse
import os
import logging
import signal
import sys
import threading
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ==================== 版本信息 ====================
VERSION = "3.0.0"
PROGRAM_NAME = "GitHub Hosts Ultimate"

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_hosts_ultimate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置区 ====================

# 域名分级配置
DOMAIN_LEVELS = {
    'core': [
        # ===== 核心服务（20个）=====
        'github.com', 'api.github.com', 'gist.github.com', 'codeload.github.com',
        'github.blog', 'github.community', 'github.dev', 'alive.github.com',
        'live.github.com', 'education.github.com',
        # ===== CDN与静态资源（5个）=====
        'github.githubassets.com', 'github.io', 'github.map.fastly.net',
        'github.global.ssl.fastly.net', 'githubstatus.com',
        # ===== UserContent核心（5个）=====
        'raw.githubusercontent.com', 'objects.githubusercontent.com',
        'avatars.githubusercontent.com', 'camo.githubusercontent.com',
        'user-images.githubusercontent.com',
    ],
    'extended': [
        # ===== 更多UserContent（16个）=====
        'raw.github.com', 'objects-origin.githubusercontent.com',
        'release-assets.githubusercontent.com', 'github-releases.githubusercontent.com',
        'github-registry-files.githubusercontent.com', 'avatars0.githubusercontent.com',
        'avatars1.githubusercontent.com', 'avatars2.githubusercontent.com',
        'avatars3.githubusercontent.com', 'avatars4.githubusercontent.com',
        'avatars5.githubusercontent.com', 'private-user-images.githubusercontent.com',
        'cloud.githubusercontent.com', 'desktop.githubusercontent.com',
        'favicons.githubusercontent.com', 'media.githubusercontent.com',
        'pkg-containers.githubusercontent.com',
        # ===== 包管理器（13个）=====
        'ghcr.io', 'maven.pkg.github.com', 'npm.pkg.github.com',
        'npm-proxy.pkg.github.com', 'npm-beta.pkg.github.com',
        'npm-beta-proxy.pkg.github.com', 'nuget.pkg.github.com',
        'rubygems.pkg.github.com', 'pypi.pkg.github.com',
        'swift.pkg.github.com', 'docker.pkg.github.com',
        'docker-proxy.pkg.github.com', 'containers.pkg.github.com',
        # ===== AWS S3（5个）=====
        'github-cloud.s3.amazonaws.com', 'github-com.s3.amazonaws.com',
        'github-production-release-asset-2e65be.s3.amazonaws.com',
        'github-production-user-asset-6210df.s3.amazonaws.com',
        'github-production-repository-file-5c1aeb.s3.amazonaws.com',
        # ===== Copilot（7个）=====
        'githubcopilot.com', 'api.githubcopilot.com',
        'api.individual.githubcopilot.com', 'copilot-proxy.githubusercontent.com',
        'copilot-telemetry.githubusercontent.com', 'default.exp-tas.com',
        'collector.github.com', 'central.github.com',
    ],
    'optional': [
        # ===== Actions（49个）=====
        'pipelines.actions.githubusercontent.com', 'vstoken.actions.githubusercontent.com',
        'broker.actions.githubusercontent.com', 'launch.actions.githubusercontent.com',
        'runner-auth.actions.githubusercontent.com', 'tokenghub.actions.githubusercontent.com',
        'setup-tools.actions.githubusercontent.com', 'pkg.actions.githubusercontent.com',
        'results-receiver.actions.githubusercontent.com', 'mpsghub.actions.githubusercontent.com',
        'pipelinesghubeus1.actions.githubusercontent.com', 'pipelinesghubeus2.actions.githubusercontent.com',
        'pipelinesghubeus3.actions.githubusercontent.com', 'pipelinesghubeus4.actions.githubusercontent.com',
        'pipelinesghubeus5.actions.githubusercontent.com', 'pipelinesghubeus6.actions.githubusercontent.com',
        'pipelinesghubeus7.actions.githubusercontent.com', 'pipelinesghubeus8.actions.githubusercontent.com',
        'pipelinesghubeus9.actions.githubusercontent.com', 'pipelinesghubeus10.actions.githubusercontent.com',
        'pipelinesghubeus11.actions.githubusercontent.com', 'pipelinesghubeus12.actions.githubusercontent.com',
        'pipelinesghubeus13.actions.githubusercontent.com', 'pipelinesghubeus14.actions.githubusercontent.com',
        'pipelinesghubeus15.actions.githubusercontent.com', 'pipelinesghubeus20.actions.githubusercontent.com',
        'pipelinesghubeus21.actions.githubusercontent.com', 'pipelinesghubeus22.actions.githubusercontent.com',
        'pipelinesghubeus23.actions.githubusercontent.com', 'pipelinesghubeus24.actions.githubusercontent.com',
        'pipelinesghubeus25.actions.githubusercontent.com', 'pipelinesghubeus26.actions.githubusercontent.com',
        'pipelinesproxcnc1.actions.githubusercontent.com', 'pipelinesproxcus1.actions.githubusercontent.com',
        'pipelinesproxeau1.actions.githubusercontent.com', 'pipelinesproxsdc1.actions.githubusercontent.com',
        'pipelinesproxweu1.actions.githubusercontent.com', 'pipelinesproxwus31.actions.githubusercontent.com',
        'runnerghubeus1.actions.githubusercontent.com', 'runnerghubeus20.actions.githubusercontent.com',
        'runnerghubeus21.actions.githubusercontent.com', 'runnerghubwus31.actions.githubusercontent.com',
        'runnerproxcnc1.actions.githubusercontent.com', 'runnerproxcus1.actions.githubusercontent.com',
        'runnerproxeau1.actions.githubusercontent.com', 'runnerproxsdc1.actions.githubusercontent.com',
        'runnerproxweu1.actions.githubusercontent.com', 'run-actions-1-azure-eastus.actions.githubusercontent.com',
        'run-actions-2-azure-eastus.actions.githubusercontent.com', 'run-actions-3-azure-eastus.actions.githubusercontent.com',
        # ===== Azure Blob（24个）=====
        'productionresultssa0.blob.core.windows.net', 'productionresultssa1.blob.core.windows.net',
        'productionresultssa2.blob.core.windows.net', 'productionresultssa3.blob.core.windows.net',
        'productionresultssa4.blob.core.windows.net', 'productionresultssa5.blob.core.windows.net',
        'productionresultssa6.blob.core.windows.net', 'productionresultssa7.blob.core.windows.net',
        'productionresultssa8.blob.core.windows.net', 'productionresultssa9.blob.core.windows.net',
        'productionresultssa10.blob.core.windows.net', 'productionresultssa11.blob.core.windows.net',
        'productionresultssa12.blob.core.windows.net', 'productionresultssa13.blob.core.windows.net',
        'productionresultssa14.blob.core.windows.net', 'productionresultssa15.blob.core.windows.net',
        'productionresultssa16.blob.core.windows.net', 'productionresultssa17.blob.core.windows.net',
        'productionresultssa18.blob.core.windows.net', 'productionresultssa19.blob.core.windows.net',
        'mavenregistryv2prod.blob.core.windows.net', 'npmregistryv2prod.blob.core.windows.net',
        'nugetregistryv2prod.blob.core.windows.net', 'rubygemsregistryv2prod.blob.core.windows.net',
        # ===== 其他（4个）=====
        'tuf-repo.github.com', 'fulcio.githubapp.com',
        'timestamp.githubapp.com', 'vscode.dev',
    ]
}

# DoH服务器
DOH_SERVERS = [
    'https://1.1.1.1/dns-query',
    'https://8.8.8.8/resolve',
    'https://223.5.5.5/resolve',
]

# 传统DNS服务器
DNS_SERVERS = ['1.1.1.1', '8.8.8.8', '223.5.5.5', '114.114.114.114']

# 测速配置
TCP_TEST_COUNT = 3
TCP_TIMEOUT = 2
TCP_PORT = 443
MAX_WORKERS = 10
TOP_IP_COUNT = 3

# 缓存配置
CACHE_FILE = '.github_hosts_cache.json'
CACHE_ENABLED = True

# Daemon配置
DEFAULT_DAEMON_INTERVAL = 600  # 10分钟
DEFAULT_HTTP_PORT = 8080

# 全局状态
class GlobalState:
    """全局状态管理"""
    def __init__(self):
        self.results = {}
        self.stats = {}
        self.last_update = None
        self.is_running = True
        self.lock = threading.Lock()

    def update_results(self, results):
        with self.lock:
            self.results = results
            self.last_update = datetime.now()

    def get_results(self):
        with self.lock:
            return self.results.copy()

    def update_stats(self, stats):
        with self.lock:
            self.stats = stats

    def get_stats(self):
        with self.lock:
            return self.stats.copy()

    def stop(self):
        self.is_running = False

global_state = GlobalState()

# ==================== DoH查询模块 ====================

def query_dns_doh(domain: str, doh_server: str) -> List[str]:
    """使用DNS-over-HTTPS查询"""
    try:
        import requests
        response = requests.get(
            doh_server,
            params={'name': domain, 'type': 'A'},
            headers={'accept': 'application/dns-json'},
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            return [ans['data'] for ans in data.get('Answer', []) if ans.get('type') == 1]
    except Exception as e:
        logger.debug(f"DoH查询失败 {domain} @ {doh_server}: {e}")
    return []

def query_dns_doh_all(domain: str) -> List[str]:
    """从所有DoH服务器查询"""
    all_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(DOH_SERVERS)) as executor:
        futures = [executor.submit(query_dns_doh, domain, srv) for srv in DOH_SERVERS]
        for future in concurrent.futures.as_completed(futures):
            try:
                all_ips.extend(future.result())
            except:
                pass
    return list(set(all_ips))

# ==================== 传统DNS查询 ====================

def query_dns_traditional(domain: str, dns_server: str) -> List[str]:
    """传统DNS查询"""
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = 3
        resolver.lifetime = 3
        return [str(rdata) for rdata in resolver.resolve(domain, 'A')]
    except Exception as e:
        logger.debug(f"DNS查询失败 {domain} @ {dns_server}: {e}")
    return []

def query_dns_traditional_all(domain: str) -> List[str]:
    """从所有传统DNS查询"""
    all_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(DNS_SERVERS)) as executor:
        futures = [executor.submit(query_dns_traditional, domain, srv) for srv in DNS_SERVERS]
        for future in concurrent.futures.as_completed(futures):
            try:
                all_ips.extend(future.result())
            except:
                pass
    unique_ips = list(set(all_ips))
    return [ip for ip in unique_ips if not ip.startswith(('127.', '0.', '169.254.'))]

# ==================== Web爬虫降级 ====================

def query_ipaddress_com(domain: str) -> List[str]:
    """从ipaddress.com爬取IP（第三层降级）"""
    try:
        import requests
        import re
        url = f'https://sites.ipaddress.com/{domain}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
            ips = re.findall(pattern, response.text)
            # 过滤明显错误的IP
            valid_ips = [ip for ip in ips if not ip.startswith(('127.', '0.', '255.', '169.254.'))]
            return list(set(valid_ips))[:5]  # 最多返回5个
    except Exception as e:
        logger.debug(f"Web爬虫失败 {domain}: {e}")
    return []

# ==================== 三层降级DNS查询 ====================

def get_all_ips(domain: str, use_doh: bool = True, use_web: bool = True) -> List[str]:
    """三层降级策略：DoH → 传统DNS → Web爬虫"""
    # Layer 1: DoH
    if use_doh:
        try:
            ips = query_dns_doh_all(domain)
            if ips:
                logger.debug(f"{domain} - DoH成功: {len(ips)}个IP")
                return ips
        except:
            pass

    # Layer 2: 传统DNS
    try:
        ips = query_dns_traditional_all(domain)
        if ips:
            logger.debug(f"{domain} - 传统DNS成功: {len(ips)}个IP")
            return ips
    except:
        pass

    # Layer 3: Web爬虫
    if use_web:
        try:
            ips = query_ipaddress_com(domain)
            if ips:
                logger.debug(f"{domain} - Web爬虫成功: {len(ips)}个IP")
                return ips
        except:
            pass

    return []

# ==================== TCP测速 ====================

def test_tcp_speed(ip: str, port: int = TCP_PORT, timeout: int = TCP_TIMEOUT) -> float:
    """测试TCP连接速度"""
    try:
        start = time.time()
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return (time.time() - start) * 1000
    except:
        return float('inf')

def test_tcp_latency(ip: str, count: int = TCP_TEST_COUNT) -> float:
    """多次TCP测试取中位数"""
    results = [test_tcp_speed(ip) for _ in range(count)]
    results = [r for r in results if r != float('inf')]
    if not results:
        return float('inf')
    results.sort()
    mid = len(results) // 2
    if len(results) % 2 == 0:
        return (results[mid - 1] + results[mid]) / 2
    return results[mid]

# ==================== 智能缓存 ====================

def load_cache() -> Dict:
    """加载缓存"""
    if not CACHE_ENABLED or not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache: Dict):
    """保存缓存"""
    if not CACHE_ENABLED:
        return
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"保存缓存失败: {e}")

def update_cache(domain: str, ip: str, latency: float):
    """更新缓存（滑动平均）"""
    if not CACHE_ENABLED:
        return
    cache = load_cache()
    key = f"{domain}:{ip}"
    if key not in cache:
        cache[key] = {'count': 0, 'avg_latency': 0, 'last_success': None}
    old_avg = cache[key]['avg_latency']
    count = cache[key]['count']
    cache[key]['avg_latency'] = (old_avg * count + latency) / (count + 1)
    cache[key]['count'] += 1
    cache[key]['last_success'] = datetime.now().isoformat()
    save_cache(cache)

def get_cached_ips(domain: str) -> List[Tuple[str, float]]:
    """获取缓存的IP"""
    cache = load_cache()
    results = []
    for key, data in cache.items():
        if key.startswith(f"{domain}:"):
            ip = key.split(':', 1)[1]
            results.append((ip, data['avg_latency']))
    return results

# ==================== 核心处理 ====================

def get_fastest_ips(domain: str, use_doh: bool = True, use_cache: bool = True, use_web: bool = True) -> List[Tuple[str, float]]:
    """获取最快的前N个IP"""
    logger.info(f"处理: {domain}")

    # 获取IP列表
    ips = get_all_ips(domain, use_doh, use_web)
    if use_cache:
        cached = get_cached_ips(domain)
        ips = list(set(ips + [ip for ip, _ in cached]))

    if not ips:
        logger.warning(f"{domain} - 未找到IP")
        return []

    logger.debug(f"{domain} - 找到{len(ips)}个IP")

    # 并发测速
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(ips), 5)) as executor:
        future_to_ip = {executor.submit(test_tcp_latency, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                latency = future.result()
                results[ip] = latency
                if latency != float('inf'):
                    logger.debug(f"{domain} - {ip}: {latency:.2f}ms")
                    update_cache(domain, ip, latency)
            except:
                results[ip] = float('inf')

    # 排序并返回前N个
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    valid = [(ip, lat) for ip, lat in sorted_results if lat != float('inf')]

    if valid:
        top_n = valid[:TOP_IP_COUNT]
        logger.info(f"{domain} - 最快: {', '.join([f'{ip}({lat:.0f}ms)' for ip, lat in top_n])}")
        return top_n
    elif ips:
        logger.warning(f"{domain} - 所有IP测速失败，使用默认: {ips[0]}")
        return [(ips[0], float('inf'))]
    return []

# ==================== 文件生成 ====================

def get_domain_list(level: str) -> List[str]:
    """获取域名列表"""
    if level == 'core':
        return DOMAIN_LEVELS['core']
    elif level == 'extended':
        return DOMAIN_LEVELS['core'] + DOMAIN_LEVELS['extended']
    else:  # full
        return DOMAIN_LEVELS['core'] + DOMAIN_LEVELS['extended'] + DOMAIN_LEVELS['optional']

def generate_hosts_content(results: Dict, level: str, multi_ip: bool = True) -> str:
    """生成hosts文件内容"""
    domains = get_domain_list(level)
    lines = [
        "# GitHub Hosts Ultimate",
        f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"# 版本: {VERSION}",
        f"# 域名级别: {level.upper()}",
        f"# 成功率: {len(results)}/{len(domains)} ({len(results)/len(domains)*100:.1f}%)",
        "#",
        "# ==================== GitHub Hosts Start ====================",
        ""
    ]

    for domain in domains:
        if domain in results:
            ip_list = results[domain]
            if multi_ip:
                for ip, latency in ip_list:
                    latency_str = f"# {latency:.1f}ms" if latency != float('inf') else "# timeout"
                    lines.append(f"{ip:<20} {domain:<50} {latency_str}")
            else:
                ip, latency = ip_list[0]
                latency_str = f"# {latency:.1f}ms" if latency != float('inf') else "# timeout"
                lines.append(f"{ip:<20} {domain:<50} {latency_str}")

    lines.extend(["", "# ==================== GitHub Hosts End ====================", ""])
    return '\n'.join(lines)

def generate_hosts_file(output_file: str, level: str, use_doh: bool, use_cache: bool, use_web: bool, multi_ip: bool):
    """生成hosts文件"""
    domains = get_domain_list(level)
    logger.info("=" * 70)
    logger.info(f"{PROGRAM_NAME} v{VERSION}")
    logger.info("=" * 70)
    logger.info(f"域名级别: {level.upper()} ({len(domains)}个)")
    logger.info(f"DNS方式: {'DoH' if use_doh else '传统DNS'}")
    logger.info(f"智能缓存: {'启用' if use_cache else '禁用'}")
    logger.info(f"Web降级: {'启用' if use_web else '禁用'}")
    logger.info(f"多IP轮询: {'启用' if multi_ip else '禁用'}")
    logger.info("=" * 70)

    start_time = time.time()
    results = {}
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_domain = {
            executor.submit(get_fastest_ips, domain, use_doh, use_cache, use_web): domain
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
                logger.error(f"处理失败 {domain}: {e}")

    # 生成内容
    content = generate_hosts_content(results, level, multi_ip)

    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"写入文件失败: {e}")
        return

    elapsed = time.time() - start_time

    # 统计信息
    stats = {
        'total_domains': len(domains),
        'success_count': success_count,
        'success_rate': success_count / len(domains) * 100,
        'elapsed_time': elapsed,
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'use_doh': use_doh,
        'use_cache': use_cache,
        'multi_ip': multi_ip
    }

    global_state.update_results(results)
    global_state.update_stats(stats)

    logger.info("=" * 70)
    logger.info(f"✅ Hosts文件已生成: {output_file}")
    logger.info(f"✅ 成功率: {success_count}/{len(domains)} ({stats['success_rate']:.1f}%)")
    logger.info(f"⏱️  总耗时: {elapsed:.2f}秒")
    logger.info("=" * 70)

    return results, stats

# ==================== 统计报告生成 ====================

def generate_stats_report(results: Dict, stats: Dict, output_file: str = 'stats_report.md'):
    """生成统计报告"""
    try:
        # 计算统计数据
        all_latencies = []
        for domain, ip_list in results.items():
            for ip, latency in ip_list:
                if latency != float('inf'):
                    all_latencies.append((domain, ip, latency))

        all_latencies.sort(key=lambda x: x[2])

        # 生成报告
        lines = [
            f"# GitHub Hosts 性能统计报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"## 📊 总体统计",
            f"",
            f"- **域名总数**: {stats['total_domains']}",
            f"- **成功解析**: {stats['success_count']} ({stats['success_rate']:.1f}%)",
            f"- **总耗时**: {stats['elapsed_time']:.2f}秒",
            f"- **域名级别**: {stats['level'].upper()}",
            f"",
            f"## ⚡ 性能分析",
            f"",
        ]

        if all_latencies:
            avg_latency = sum(l[2] for l in all_latencies) / len(all_latencies)
            min_latency = all_latencies[0][2]
            max_latency = all_latencies[-1][2]

            lines.extend([
                f"- **平均延迟**: {avg_latency:.2f}ms",
                f"- **最低延迟**: {min_latency:.2f}ms ({all_latencies[0][0]})",
                f"- **最高延迟**: {max_latency:.2f}ms ({all_latencies[-1][0]})",
                f"",
                f"## 🏆 Top 10 最快域名",
                f"",
                f"| 排名 | 域名 | IP | 延迟 |",
                f"|------|------|-----|------|",
            ])

            for idx, (domain, ip, latency) in enumerate(all_latencies[:10], 1):
                lines.append(f"| {idx} | {domain} | {ip} | {latency:.2f}ms |")

            lines.extend([
                f"",
                f"## 🐢 Top 10 最慢域名",
                f"",
                f"| 排名 | 域名 | IP | 延迟 |",
                f"|------|------|-----|------|",
            ])

            for idx, (domain, ip, latency) in enumerate(all_latencies[-10:][::-1], 1):
                lines.append(f"| {idx} | {domain} | {ip} | {latency:.2f}ms |")

        lines.extend([
            f"",
            f"## 📈 延迟分布",
            f"",
        ])

        if all_latencies:
            ranges = [
                (0, 50, "🟢 优秀"),
                (50, 100, "🟡 良好"),
                (100, 200, "🟠 一般"),
                (200, float('inf'), "🔴 较慢")
            ]

            for min_l, max_l, label in ranges:
                count = len([l for _, _, l in all_latencies if min_l <= l < max_l])
                pct = count / len(all_latencies) * 100
                lines.append(f"- **{label}** ({min_l}-{max_l}ms): {count}个 ({pct:.1f}%)")

        lines.extend([
            f"",
            f"---",
            f"",
            f"*报告由 {PROGRAM_NAME} v{VERSION} 生成*",
        ])

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"📊 统计报告已生成: {output_file}")

    except Exception as e:
        logger.error(f"生成统计报告失败: {e}")

# ==================== HTTP API服务 ====================

class HostsHTTPHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""

    def log_message(self, format, *args):
        """重写日志方法"""
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            if path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self._generate_index_page().encode())

            elif path == '/hosts':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                results = global_state.get_results()
                if results:
                    content = generate_hosts_content(results, 'extended', multi_ip=True)
                    self.wfile.write(content.encode())
                else:
                    self.wfile.write(b"# Hosts file not generated yet")

            elif path == '/stats':
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                stats = global_state.get_stats()
                self.wfile.write(json.dumps(stats, indent=2, ensure_ascii=False).encode())

            elif path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                health = {
                    'status': 'healthy',
                    'version': VERSION,
                    'last_update': global_state.last_update.isoformat() if global_state.last_update else None
                }
                self.wfile.write(json.dumps(health).encode())

            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Internal Server Error: {e}".encode())

    def _generate_index_page(self) -> str:
        """生成首页"""
        stats = global_state.get_stats()
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{PROGRAM_NAME} v{VERSION}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        .stats {{ background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .endpoint {{ background: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 4px; }}
        .endpoint code {{ background: #fff; padding: 5px 10px; border-radius: 3px; }}
        a {{ color: #2196F3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{PROGRAM_NAME}</h1>
        <p><strong>版本</strong>: {VERSION}</p>
        <p><strong>状态</strong>: 🟢 运行中</p>

        <div class="stats">
            <h3>📊 统计信息</h3>
            <p><strong>最后更新</strong>: {global_state.last_update.strftime('%Y-%m-%d %H:%M:%S') if global_state.last_update else '未生成'}</p>
            {f'<p><strong>成功率</strong>: {stats["success_count"]}/{stats["total_domains"]} ({stats["success_rate"]:.1f}%)</p>' if stats else ''}
            {f'<p><strong>耗时</strong>: {stats["elapsed_time"]:.2f}秒</p>' if stats else ''}
        </div>

        <h3>🔗 API端点</h3>
        <div class="endpoint">
            <strong>GET /hosts</strong><br>
            获取最新的hosts文件<br>
            <code>curl http://localhost:{DEFAULT_HTTP_PORT}/hosts</code>
        </div>

        <div class="endpoint">
            <strong>GET /stats</strong><br>
            获取统计信息（JSON格式）<br>
            <code>curl http://localhost:{DEFAULT_HTTP_PORT}/stats</code>
        </div>

        <div class="endpoint">
            <strong>GET /health</strong><br>
            健康检查<br>
            <code>curl http://localhost:{DEFAULT_HTTP_PORT}/health</code>
        </div>

        <h3>📖 使用方法</h3>
        <pre><code># 下载hosts文件
curl http://localhost:{DEFAULT_HTTP_PORT}/hosts >> /etc/hosts

# 查看统计
curl http://localhost:{DEFAULT_HTTP_PORT}/stats | jq</code></pre>
    </div>
</body>
</html>"""

def start_http_server(port: int):
    """启动HTTP服务器"""
    try:
        server = HTTPServer(('0.0.0.0', port), HostsHTTPHandler)
        logger.info(f"🌐 HTTP服务已启动: http://0.0.0.0:{port}")
        logger.info(f"   - 访问 http://localhost:{port}/ 查看状态")
        logger.info(f"   - 访问 http://localhost:{port}/hosts 下载hosts")
        logger.info(f"   - 访问 http://localhost:{port}/stats 查看统计")
        server.serve_forever()
    except Exception as e:
        logger.error(f"HTTP服务器启动失败: {e}")

# ==================== Daemon模式 ====================

def daemon_worker(args):
    """Daemon工作线程"""
    logger.info(f"🔄 Daemon模式启动，更新间隔: {args.interval}秒")

    while global_state.is_running:
        try:
            logger.info("开始更新hosts...")
            generate_hosts_file(
                args.output,
                args.level,
                not args.no_doh,
                not args.no_cache,
                not args.no_web,
                not args.no_multi_ip
            )

            if args.report:
                results = global_state.get_results()
                stats = global_state.get_stats()
                generate_stats_report(results, stats, 'stats_report.md')

            logger.info(f"✅ 更新完成，下次更新时间: {args.interval}秒后")

            # 等待下一次更新
            for _ in range(args.interval):
                if not global_state.is_running:
                    break
                time.sleep(1)

        except Exception as e:
            logger.error(f"Daemon更新失败: {e}")
            time.sleep(60)  # 失败后等待1分钟

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info("\n收到停止信号，正在退出...")
    global_state.stop()
    sys.exit(0)

# ==================== 主程序 ====================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description=f'{PROGRAM_NAME} v{VERSION}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # CLI模式（一次性生成）
  python %(prog)s --level=extended

  # Daemon模式（持续服务）
  python %(prog)s --daemon --interval=600 --port=8080

  # 生成统计报告
  python %(prog)s --level=full --report
        """
    )

    parser.add_argument('--level', choices=['core', 'extended', 'full'], default='extended',
                        help='域名级别 [默认: extended]')
    parser.add_argument('--output', default='github_hosts_ultimate',
                        help='输出文件路径 [默认: github_hosts_ultimate]')
    parser.add_argument('--no-doh', action='store_true', help='禁用DoH')
    parser.add_argument('--no-cache', action='store_true', help='禁用缓存')
    parser.add_argument('--no-web', action='store_true', help='禁用Web爬虫降级')
    parser.add_argument('--no-multi-ip', action='store_true', help='禁用多IP轮询')
    parser.add_argument('--report', action='store_true', help='生成统计报告')

    # Daemon模式参数
    parser.add_argument('--daemon', action='store_true', help='Daemon模式（持续运行）')
    parser.add_argument('--interval', type=int, default=DEFAULT_DAEMON_INTERVAL,
                        help=f'Daemon更新间隔（秒） [默认: {DEFAULT_DAEMON_INTERVAL}]')
    parser.add_argument('--port', type=int, default=DEFAULT_HTTP_PORT,
                        help=f'HTTP服务端口 [默认: {DEFAULT_HTTP_PORT}]')

    parser.add_argument('--version', action='version', version=f'{PROGRAM_NAME} v{VERSION}')

    args = parser.parse_args()

    # 检查依赖
    try:
        import dns.resolver
        import requests
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.error("请安装: pip install dnspython requests")
        sys.exit(1)

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if args.daemon:
            # Daemon模式
            logger.info(f"🚀 启动 {PROGRAM_NAME} v{VERSION} - Daemon模式")

            # 启动HTTP服务器线程
            http_thread = threading.Thread(target=start_http_server, args=(args.port,), daemon=True)
            http_thread.start()

            # 运行Daemon工作线程
            daemon_worker(args)

        else:
            # CLI模式
            logger.info(f"🚀 启动 {PROGRAM_NAME} v{VERSION} - CLI模式")

            results, stats = generate_hosts_file(
                args.output,
                args.level,
                not args.no_doh,
                not args.no_cache,
                not args.no_web,
                not args.no_multi_ip
            )

            if args.report:
                generate_stats_report(results, stats, 'stats_report.md')

    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
