#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast GitHub Hosts - 持久化安装脚本
跨平台自动安装和更新 GitHub Hosts
支持 Windows/Linux/macOS
"""

import os
import sys
import platform
import shutil
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# ==================== 配置区 ====================

# 区块标记（用于识别和替换）
BEGIN_MARKER = "# BEGIN FAST-GITHUB-HOSTS"
END_MARKER = "# END FAST-GITHUB-HOSTS"

# 跨平台 hosts 文件路径
HOSTS_PATHS = {
    'Windows': r'C:\Windows\System32\drivers\etc\hosts',
    'Linux': '/etc/hosts',
    'Darwin': '/etc/hosts',  # macOS
}

# DNS 刷新命令
FLUSH_DNS_COMMANDS = {
    'Windows': ['ipconfig', '/flushdns'],
    'Linux': [
        # 尝试多种方式，按优先级
        ['systemctl', 'restart', 'systemd-resolved'],
        ['systemctl', 'restart', 'nscd'],
        ['service', 'nscd', 'restart'],
    ],
    'Darwin': [  # macOS
        ['dscacheutil', '-flushcache'],
        ['killall', '-HUP', 'mDNSResponder'],
    ],
}

# ==================== 工具函数 ====================

def get_system():
    """获取操作系统类型"""
    return platform.system()


def get_hosts_path():
    """获取当前系统的 hosts 文件路径"""
    system = get_system()
    if system not in HOSTS_PATHS:
        raise RuntimeError(f"不支持的操作系统: {system}")
    return HOSTS_PATHS[system]


def check_admin():
    """检查是否有管理员/root权限"""
    system = get_system()

    if system == 'Windows':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:  # Linux/macOS
        return os.geteuid() == 0


def backup_hosts(hosts_path):
    """备份 hosts 文件"""
    backup_path = f"{hosts_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(hosts_path, backup_path)
        print(f"✅ 已备份原 hosts 文件: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  备份失败: {e}")
        return None


def read_hosts_file(hosts_path):
    """读取 hosts 文件内容"""
    try:
        with open(hosts_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 无法读取 hosts 文件: {e}")
        sys.exit(1)


def write_hosts_file(hosts_path, content):
    """写入 hosts 文件"""
    try:
        with open(hosts_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print(f"✅ 已更新 hosts 文件: {hosts_path}")
        return True
    except Exception as e:
        print(f"❌ 无法写入 hosts 文件: {e}")
        return False


def remove_old_block(content):
    """移除旧的 GitHub Hosts 区块"""
    lines = content.split('\n')
    result = []
    in_block = False

    for line in lines:
        if line.strip() == BEGIN_MARKER:
            in_block = True
            continue
        if line.strip() == END_MARKER:
            in_block = False
            continue
        if not in_block:
            result.append(line)

    return '\n'.join(result)


def generate_hosts_block(github_hosts_file):
    """生成带标记的 GitHub Hosts 区块"""
    try:
        with open(github_hosts_file, 'r', encoding='utf-8') as f:
            github_content = f.read().strip()
    except Exception as e:
        print(f"❌ 无法读取 GitHub hosts 文件: {e}")
        sys.exit(1)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    block = f"""
{BEGIN_MARKER}
# Auto-generated GitHub Hosts
# Update time: {timestamp}
# DO NOT EDIT THIS BLOCK MANUALLY
{github_content}
{END_MARKER}
"""
    return block


def merge_hosts(original_content, github_hosts_file):
    """合并 hosts 文件（替换旧区块）"""
    # 1. 移除旧的 GitHub Hosts 区块
    cleaned_content = remove_old_block(original_content)

    # 2. 移除末尾多余空行
    cleaned_content = cleaned_content.rstrip('\n')

    # 3. 生成新的 GitHub Hosts 区块
    github_block = generate_hosts_block(github_hosts_file)

    # 4. 合并内容
    merged_content = cleaned_content + '\n' + github_block + '\n'

    return merged_content


def flush_dns():
    """刷新 DNS 缓存"""
    system = get_system()
    commands = FLUSH_DNS_COMMANDS.get(system, [])

    if not commands:
        print("⚠️  未知系统，跳过 DNS 刷新")
        return False

    # 如果是单个命令
    if commands and isinstance(commands[0], str):
        commands = [commands]

    # 尝试执行命令（按优先级）
    success = False
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ DNS 缓存已刷新: {' '.join(cmd)}")
                success = True
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️  刷新命令失败 ({' '.join(cmd)}): {e}")
            continue

    if not success:
        print("⚠️  DNS 刷新失败，请手动刷新")
        print_flush_instructions()

    return success


def print_flush_instructions():
    """打印手动刷新 DNS 的说明"""
    system = get_system()

    instructions = {
        'Windows': '手动刷新: ipconfig /flushdns',
        'Linux': '手动刷新: sudo systemctl restart systemd-resolved',
        'Darwin': '手动刷新: sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder',
    }

    if system in instructions:
        print(f"💡 {instructions[system]}")


def uninstall_hosts(hosts_path):
    """卸载 GitHub Hosts（移除区块）"""
    print("🗑️  开始卸载 GitHub Hosts...")

    # 读取当前 hosts
    original_content = read_hosts_file(hosts_path)

    # 检查是否存在区块
    if BEGIN_MARKER not in original_content:
        print("⚠️  未找到 GitHub Hosts 区块，可能已卸载")
        return False

    # 备份
    backup_hosts(hosts_path)

    # 移除区块
    cleaned_content = remove_old_block(original_content)
    cleaned_content = cleaned_content.rstrip('\n') + '\n'

    # 写入
    if write_hosts_file(hosts_path, cleaned_content):
        print("✅ GitHub Hosts 已卸载")
        flush_dns()
        return True

    return False


def install_hosts(github_hosts_file, hosts_path, skip_backup=False):
    """安装/更新 GitHub Hosts"""
    print(f"🚀 开始安装 GitHub Hosts...")
    print(f"📋 系统: {get_system()}")
    print(f"📂 Hosts 路径: {hosts_path}")
    print(f"📄 GitHub Hosts: {github_hosts_file}")
    print()

    # 检查 GitHub hosts 文件是否存在
    if not os.path.exists(github_hosts_file):
        print(f"❌ 文件不存在: {github_hosts_file}")
        sys.exit(1)

    # 读取原始 hosts
    original_content = read_hosts_file(hosts_path)

    # 备份（可选）
    if not skip_backup:
        backup_hosts(hosts_path)

    # 合并内容
    merged_content = merge_hosts(original_content, github_hosts_file)

    # 写入 hosts
    if not write_hosts_file(hosts_path, merged_content):
        print("❌ 安装失败")
        sys.exit(1)

    # 刷新 DNS
    flush_dns()

    print()
    print("=" * 70)
    print("✅ GitHub Hosts 安装成功！")
    print("=" * 70)
    print()
    print("💡 提示:")
    print("  - 重新运行此脚本将自动更新 hosts")
    print("  - 使用 --uninstall 可以卸载")
    print("  - 配合 cron/Task Scheduler 可实现自动更新")
    print()


def show_cron_examples():
    """显示 cron 配置示例"""
    system = get_system()
    script_path = os.path.abspath(__file__)
    github_hosts = os.path.join(os.path.dirname(script_path), 'github_hosts_pro')

    print("=" * 70)
    print("⏰ Cron 定时任务配置示例")
    print("=" * 70)
    print()

    if system in ['Linux', 'Darwin']:
        print("1️⃣  编辑 crontab:")
        print("   sudo crontab -e")
        print()
        print("2️⃣  添加以下行（每天凌晨3点更新）:")
        print(f"   0 3 * * * cd {os.path.dirname(script_path)} && python3 {script_path} --input {github_hosts} --skip-backup")
        print()
        print("3️⃣  其他频率示例:")
        print("   每6小时:  0 */6 * * *")
        print("   每12小时: 0 */12 * * *")
        print("   每周一:   0 3 * * 1")

    elif system == 'Windows':
        print("使用 Task Scheduler (任务计划程序):")
        print()
        print("1️⃣  打开任务计划程序")
        print("2️⃣  创建基本任务")
        print("3️⃣  设置触发器（如每天凌晨3点）")
        print("4️⃣  操作设置为:")
        print(f"   程序: python")
        print(f"   参数: {script_path} --input {github_hosts} --skip-backup")
        print(f"   起始于: {os.path.dirname(script_path)}")
        print()
        print("5️⃣  勾选 \"使用最高权限运行\"")

    print()


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description='Fast GitHub Hosts - 持久化安装脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  安装/更新 GitHub Hosts:
    sudo python3 install_hosts.py --input github_hosts_pro

  卸载 GitHub Hosts:
    sudo python3 install_hosts.py --uninstall

  查看 Cron 配置示例:
    python3 install_hosts.py --cron-example

  跳过备份（用于自动任务）:
    sudo python3 install_hosts.py --input github_hosts_pro --skip-backup
        """
    )

    parser.add_argument(
        '--input',
        default='github_hosts_pro',
        help='GitHub hosts 文件路径 (默认: github_hosts_pro)'
    )

    parser.add_argument(
        '--uninstall',
        action='store_true',
        help='卸载 GitHub Hosts（移除区块）'
    )

    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='跳过备份（用于自动任务）'
    )

    parser.add_argument(
        '--cron-example',
        action='store_true',
        help='显示 Cron 配置示例'
    )

    args = parser.parse_args()

    # 显示 Cron 示例
    if args.cron_example:
        show_cron_examples()
        sys.exit(0)

    # 检查权限
    if not check_admin():
        print("=" * 70)
        print("❌ 权限不足")
        print("=" * 70)
        print()
        system = get_system()
        if system == 'Windows':
            print("请以管理员身份运行此脚本:")
            print("  右键点击 PowerShell/CMD → 以管理员身份运行")
        else:
            print("请使用 sudo 运行此脚本:")
            print(f"  sudo python3 {sys.argv[0]} {' '.join(sys.argv[1:])}")
        print()
        sys.exit(1)

    # 获取 hosts 路径
    hosts_path = get_hosts_path()

    # 卸载模式
    if args.uninstall:
        uninstall_hosts(hosts_path)
        sys.exit(0)

    # 安装/更新模式
    install_hosts(args.input, hosts_path, args.skip_backup)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
