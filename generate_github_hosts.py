#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Hosts 自动生成工具 - Ultra版本
功能：DNS查询 + Ping+TCP测速 + 自动生成hosts文件
作者：基于GitHub Meta API和实际测试
"""

import dns.resolver
import subprocess
import socket
import concurrent.futures
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import sys

# ==================== 配置区 ====================

# GitHub完整域名列表（基于官方API + 实际测试）- 共141个
GITHUB_DOMAINS = [
    # ===== 核心服务（12个）- P0必须 =====
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
    'collector.github.com',
    'central.github.com',

    # ===== CDN与静态资源（5个）- P0必须 =====
    'github.githubassets.com',
    'github.io',
    'github.map.fastly.net',
    'github.global.ssl.fastly.net',
    'githubstatus.com',

    # ===== UserContent系列（21个）- P0必须 =====
    'raw.githubusercontent.com',
    'raw.github.com',
    'objects.githubusercontent.com',
    'objects-origin.githubusercontent.com',
    'release-assets.githubusercontent.com',
    'github-releases.githubusercontent.com',
    'github-registry-files.githubusercontent.com',
    'avatars.githubusercontent.com',
    'avatars0.githubusercontent.com',
    'avatars1.githubusercontent.com',
    'avatars2.githubusercontent.com',
    'avatars3.githubusercontent.com',
    'avatars4.githubusercontent.com',
    'avatars5.githubusercontent.com',
    'camo.githubusercontent.com',
    'user-images.githubusercontent.com',
    'private-user-images.githubusercontent.com',
    'cloud.githubusercontent.com',
    'desktop.githubusercontent.com',
    'favicons.githubusercontent.com',
    'media.githubusercontent.com',
    'pkg-containers.githubusercontent.com',

    # ===== 包管理器（12个）- P0必须 =====
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

    # ===== AWS S3存储（5个）- P1重要 =====
    'github-cloud.s3.amazonaws.com',
    'github-com.s3.amazonaws.com',
    'github-production-release-asset-2e65be.s3.amazonaws.com',
    'github-production-user-asset-6210df.s3.amazonaws.com',
    'github-production-repository-file-5c1aeb.s3.amazonaws.com',

    # ===== GitHub Copilot（6个）- P1重要 =====
    'githubcopilot.com',
    'api.githubcopilot.com',
    'api.individual.githubcopilot.com',
    'copilot-proxy.githubusercontent.com',
    'copilot-telemetry.githubusercontent.com',
    'default.exp-tas.com',

    # ===== GitHub Actions核心（9个）- P1重要 =====
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

    # ===== Actions Pipelines（28个）- P1重要 =====
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

    # ===== Actions Runners（12个）- P1重要 =====
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

    # ===== Azure Blob存储 - Actions结果（20个）- P1重要 =====
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

    # ===== Azure Blob存储 - 包管理器（4个）- P1重要 =====
    'mavenregistryv2prod.blob.core.windows.net',
    'npmregistryv2prod.blob.core.windows.net',
    'nugetregistryv2prod.blob.core.windows.net',
    'rubygemsregistryv2prod.blob.core.windows.net',

    # ===== 安全认证（3个）- P2可选 =====
    'tuf-repo.github.com',
    'fulcio.githubapp.com',
    'timestamp.githubapp.com',

    # ===== 开发工具（1个）- P2可选 =====
    'vscode.dev',
]

# DNS服务器列表（多源查询）
DNS_SERVERS = [
    '1.1.1.1',          # Cloudflare DNS
    '8.8.8.8',          # Google DNS
    '223.5.5.5',        # 阿里DNS
    '114.114.114.114',  # 114DNS
]

# 测速配置
PING_COUNT = 2          # Ping次数
TCP_TIMEOUT = 2         # TCP连接超时（秒）
TCP_PORT = 443          # 测试端口
MAX_WORKERS = 10        # 最大并发数

# ==================== DNS查询模块 ====================

def query_dns(domain: str, dns_server: str) -> List[str]:
    """
    使用指定DNS服务器查询域名的A记录

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


def get_all_ips(domain: str) -> List[str]:
    """
    从多个DNS服务器获取IP并去重

    Args:
        domain: 域名

    Returns:
        去重后的IP地址列表
    """
    all_ips = []

    # 并发查询多个DNS服务器
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(DNS_SERVERS)) as executor:
        futures = [
            executor.submit(query_dns, domain, dns_server)
            for dns_server in DNS_SERVERS
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                ips = future.result()
                all_ips.extend(ips)
            except Exception as e:
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


# ==================== 测速模块 ====================

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
    except Exception as e:
        return float('inf')


def test_ping(ip: str, count: int = PING_COUNT) -> float:
    """
    测试ICMP Ping延迟（毫秒）

    Args:
        ip: IP地址
        count: Ping次数

    Returns:
        平均延迟（毫秒），失败返回inf
    """
    try:
        # Linux/Mac使用-c，Windows使用-n
        param = '-n' if sys.platform.startswith('win') else '-c'
        cmd = ['ping', param, str(count), '-W', '2', ip]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            output = result.stdout
            # 解析平均延迟
            if sys.platform.startswith('win'):
                # Windows: Average = XXms
                if 'Average' in output:
                    avg_line = [line for line in output.split('\n') if 'Average' in line][0]
                    avg_time = float(avg_line.split('=')[-1].strip().replace('ms', ''))
                    return avg_time
            else:
                # Linux/Mac: min/avg/max/mdev = X.XXX/Y.YYY/Z.ZZZ/W.WWW ms
                if 'avg' in output or 'min/' in output:
                    stats_line = [line for line in output.split('\n') if '/' in line and 'ms' in line]
                    if stats_line:
                        # 提取平均值（第二个数字）
                        parts = stats_line[0].split('=')[-1].strip().split('/')
                        if len(parts) >= 2:
                            avg_time = float(parts[1])
                            return avg_time
        return float('inf')
    except Exception as e:
        return float('inf')


def test_ip_comprehensive(ip: str) -> float:
    """
    综合测试：Ping + TCP

    Args:
        ip: IP地址

    Returns:
        综合得分（越小越好），失败返回inf
    """
    ping_time = test_ping(ip, count=PING_COUNT)
    tcp_time = test_tcp_speed(ip, port=TCP_PORT, timeout=TCP_TIMEOUT)

    # 如果都失败，返回无穷大
    if ping_time == float('inf') and tcp_time == float('inf'):
        return float('inf')

    # 综合评分：Ping权重60%，TCP权重40%
    ping_score = ping_time if ping_time != float('inf') else 1000
    tcp_score = tcp_time if tcp_time != float('inf') else 1000

    final_score = ping_score * 0.6 + tcp_score * 0.4

    return final_score


# ==================== 核心处理模块 ====================

def get_fastest_ip(domain: str) -> Tuple[Optional[str], float]:
    """
    获取域名的最快IP

    Args:
        domain: 域名

    Returns:
        (最快IP, 延迟分数) 或 (None, inf)
    """
    print(f"🔍 正在处理: {domain}")

    # 1. 获取所有IP
    ips = get_all_ips(domain)

    if not ips:
        print(f"  ❌ 未找到IP")
        return None, float('inf')

    print(f"  📡 找到 {len(ips)} 个IP: {', '.join(ips[:3])}{'...' if len(ips) > 3 else ''}")

    # 2. 并发测速
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(ips), 5)) as executor:
        future_to_ip = {
            executor.submit(test_ip_comprehensive, ip): ip
            for ip in ips
        }

        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                score = future.result()
                results[ip] = score
                if score != float('inf'):
                    print(f"  ⚡ {ip}: {score:.2f}ms")
            except Exception as e:
                results[ip] = float('inf')

    # 3. 选择最快的IP
    if results:
        fastest_ip = min(results, key=results.get)
        fastest_score = results[fastest_ip]

        if fastest_score != float('inf'):
            print(f"  ✅ 最快IP: {fastest_ip} ({fastest_score:.2f}ms)")
            return fastest_ip, fastest_score
        else:
            # 所有IP都测速失败，返回第一个
            print(f"  ⚠️  所有IP测速失败，使用默认: {ips[0]}")
            return ips[0], float('inf')

    print(f"  ⚠️  测速失败，使用默认: {ips[0]}")
    return ips[0], float('inf')


# ==================== 文件生成模块 ====================

def generate_hosts_file(output_file: str = 'ultra_hosts'):
    """
    生成hosts文件

    Args:
        output_file: 输出文件路径
    """
    print("=" * 70)
    print("🚀 GitHub Hosts 自动生成工具 - Ultra版本")
    print("=" * 70)
    print(f"📋 域名总数: {len(GITHUB_DOMAINS)}")
    print(f"🌐 DNS服务器: {', '.join(DNS_SERVERS)}")
    print(f"⚡ 测速方法: Ping + TCP")
    print("=" * 70)
    print()

    # 开始时间
    start_time = time.time()

    # 并发处理所有域名
    results = {}
    success_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_domain = {
            executor.submit(get_fastest_ip, domain): domain
            for domain in GITHUB_DOMAINS
        }

        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                ip, score = future.result()
                if ip:
                    results[domain] = (ip, score)
                    success_count += 1
            except Exception as e:
                print(f"❌ 处理失败: {domain} - {e}")

    # 生成hosts文件内容
    hosts_content = []
    hosts_content.append("# Ultra GitHub Hosts - 快速版")
    hosts_content.append(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    hosts_content.append(f"# 域名总数: {success_count}/{len(GITHUB_DOMAINS)}")
    hosts_content.append("# 方法: DNS查询 + Ping+TCP测速")
    hosts_content.append("#")
    hosts_content.append("# ==================== Start ====================")
    hosts_content.append("")

    # 按域名排序输出
    for domain in GITHUB_DOMAINS:
        if domain in results:
            ip, score = results[domain]
            # 格式化：IP左对齐20个字符
            hosts_content.append(f"{ip:<20} {domain}")

    hosts_content.append("")
    hosts_content.append("# ==================== End ====================")
    hosts_content.append("")

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(hosts_content))

    # 统计信息
    elapsed_time = time.time() - start_time

    print()
    print("=" * 70)
    print(f"✅ Hosts文件已生成: {output_file}")
    print(f"✅ 成功获取: {success_count}/{len(GITHUB_DOMAINS)} 个域名")
    print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
    print("=" * 70)
    print()
    print("📝 使用方法:")
    print("  Linux/Mac: sudo cp ultra_hosts /etc/hosts")
    print("  Windows:   复制到 C:\\Windows\\System32\\drivers\\etc\\hosts")
    print()
    print("🔄 刷新DNS:")
    print("  Linux:   sudo systemd-resolve --flush-caches")
    print("  Mac:     sudo killall -HUP mDNSResponder")
    print("  Windows: ipconfig /flushdns")
    print()


# ==================== 主程序 ====================

if __name__ == '__main__':
    try:
        # 检查依赖
        try:
            import dns.resolver
        except ImportError:
            print("❌ 缺少依赖: dnspython")
            print("📦 请安装: pip install dnspython")
            sys.exit(1)

        # 生成hosts文件
        generate_hosts_file()

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
