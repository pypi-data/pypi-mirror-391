#!/usr/bin/env python3
"""
fastuv 命令行接口

提供 fastuv install 和 fastuv uninstall 命令
"""

import sys
import argparse
from typing import Optional

from .installer import UVInstaller
from .uninstaller import UVUninstaller


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="fastuv",
        description="快速 uv 安装器 - 预配置国内镜像的 uv 安装工具"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # install 命令
    install_parser = subparsers.add_parser("install", help="安装 uv 并配置国内镜像")
    install_parser.add_argument(
        "--version",
        help="指定 uv 版本 (默认: latest)"
    )
    install_parser.add_argument(
        "--proxy",
        default="https://ghfast.top",
        help="下载代理 (默认: https://ghfast.top)"
    )
    install_parser.add_argument(
        "--mirror",
        default="https://pypi.tuna.tsinghua.edu.cn/simple/",
        help="PyPI 镜像源 (默认: 清华源)"
    )
    install_parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="不安装 conda 环境联动 hooks"
    )

    # uninstall 命令
    uninstall_parser = subparsers.add_parser("uninstall", help="卸载 uv 和相关配置")
    uninstall_parser.add_argument(
        "--all",
        action="store_true",
        help="删除所有配置文件和缓存"
    )

    return parser


def cmd_install(args) -> int:
    """处理安装命令"""
    try:
        installer = UVInstaller(
            download_proxy=args.proxy,
            pypi_mirror=args.mirror,
            version=args.version
        )

        print("[开始] 开始安装 uv...")

        # 执行安装
        success = installer.install()

        if success:
            # 安装 conda hooks（除非用户明确禁止）
            if not args.no_hooks:
                print("[配置] 配置 conda 环境联动...")
                installer.install_conda_hooks()

            print("[完成] uv 安装完成！")
            print("[提示] 请运行以下命令或重启终端以使用 uv:")
            print("   source ~/.bashrc  # 或 ~/.zshrc")
            return 0
        else:
            print("[错误] uv 安装失败")
            return 1

    except Exception as e:
        print(f"[错误] 安装过程中发生错误: {e}")
        return 1


def cmd_uninstall(args) -> int:
    """处理卸载命令"""
    try:
        uninstaller = UVUninstaller()

        print("[开始] 开始卸载 uv...")

        success = uninstaller.uninstall(remove_all=args.all)

        if success:
            print("[完成] uv 卸载完成！")
            if args.all:
                print("[清理] 所有配置文件和缓存已清理")
            return 0
        else:
            print("[错误] uv 卸载失败")
            return 1

    except Exception as e:
        print(f"[错误] 卸载过程中发生错误: {e}")
        return 1


def main() -> int:
    """主入口函数"""
    parser = create_parser()

    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args = parser.parse_args()

    if args.command == "install":
        return cmd_install(args)
    elif args.command == "uninstall":
        return cmd_uninstall(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())