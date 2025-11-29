#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Hosts 服务化工具
功能：Daemon模式 + HTTP API
基于：generate_github_hosts_ultimate.py
版本：1.0.0
"""

import signal
import sys
import threading
import time
import json
import argparse
import logging
from datetime import datetime
from typing import Dict
from http.server import HTTPServer, BaseHTTPRequestHandler

# 导入生成模块
from generate_github_hosts_ultimate import (
    VERSION as GENERATOR_VERSION,
    PROGRAM_NAME as GENERATOR_NAME,
    generate_hosts_file,
    generate_hosts_content,
    generate_stats_report
)

# ==================== 版本信息 ====================
VERSION = "1.0.0"
PROGRAM_NAME = "GitHub Hosts Service"

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_hosts_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================
DEFAULT_DAEMON_INTERVAL = 600  # 10分钟
DEFAULT_HTTP_PORT = 8080

# ==================== 全局状态管理 ====================

class GlobalState:
    """全局状态管理（线程安全）"""
    def __init__(self):
        self.results = {}
        self.stats = {}
        self.last_update = None
        self.is_running = True
        self.lock = threading.Lock()

    def update_results(self, results):
        """更新生成结果"""
        with self.lock:
            self.results = results
            self.last_update = datetime.now()

    def get_results(self):
        """获取生成结果"""
        with self.lock:
            return self.results.copy()

    def update_stats(self, stats):
        """更新统计信息"""
        with self.lock:
            self.stats = stats

    def get_stats(self):
        """获取统计信息"""
        with self.lock:
            return self.stats.copy()

    def stop(self):
        """停止服务"""
        self.is_running = False

global_state = GlobalState()

# ==================== HTTP API服务 ====================

class HostsHTTPHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""

    def log_message(self, format, *args):
        """重写日志方法"""
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """处理GET请求"""
        path = self.path

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
                    'service_version': VERSION,
                    'generator_version': GENERATOR_VERSION,
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
        <p><strong>服务版本</strong>: {VERSION}</p>
        <p><strong>生成器版本</strong>: {GENERATOR_VERSION} ({GENERATOR_NAME})</p>
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
            results, stats = generate_hosts_file(
                args.output,
                args.level,
                not args.no_doh,
                not args.no_cache,
                not args.no_web,
                not args.no_multi_ip
            )

            # 更新全局状态
            global_state.update_results(results)
            global_state.update_stats(stats)

            if args.report:
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
  # 启动服务（默认配置）
  python %(prog)s

  # 自定义更新间隔和端口
  python %(prog)s --interval=300 --port=9090

  # 指定域名级别和输出文件
  python %(prog)s --level=full --output=/etc/github_hosts
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

    parser.add_argument('--interval', type=int, default=DEFAULT_DAEMON_INTERVAL,
                        help=f'更新间隔（秒） [默认: {DEFAULT_DAEMON_INTERVAL}]')
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
        logger.info(f"🚀 启动 {PROGRAM_NAME} v{VERSION}")
        logger.info(f"📦 使用生成器: {GENERATOR_NAME} v{GENERATOR_VERSION}")

        # 启动HTTP服务器线程
        http_thread = threading.Thread(target=start_http_server, args=(args.port,), daemon=True)
        http_thread.start()

        # 运行Daemon工作线程
        daemon_worker(args)

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
