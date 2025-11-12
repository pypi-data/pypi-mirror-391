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
        help="不安装 conda 环境联动 hooks (默认)"
    )
    install_parser.add_argument(
        "--hooks-only",
        action="store_true",
        help="仅安装 conda 环境联动 hooks"
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
        # 处理 hooks-only 模式
        if args.hooks_only:
            print("=" * 60)
            print("fastuv - Conda 环境联动配置")
            print("=" * 60)

            installer = UVInstaller()
            installer.install_conda_hooks()

            print("-" * 60)
            print("[完成] Conda 环境联动配置完成")
            print("[说明] 已配置 Shell 以自动检测 Conda 环境")
            print("[操作] 请重启终端或执行 source ~/.bashrc")
            print("=" * 60)
            return 0

        # 正常安装模式
        installer = UVInstaller(
            download_proxy=args.proxy,
            pypi_mirror=args.mirror,
            version=args.version
        )

        print("=" * 60)
        print("fastuv - UV 快速安装器")
        print("=" * 60)
        print(f"[信息] 目标平台: {installer.platform}")
        print(f"[信息] UV版本: {installer.version}")
        print(f"[信息] 下载代理: {installer.download_proxy}")
        print(f"[信息] PyPI镜像: {installer.pypi_mirror}")
        print("-" * 60)

        # 执行安装
        success = installer.install()

        if success:
            print("-" * 60)
            print("[完成] UV 安装成功！")

            # conda 联动提示（默认不安装）
            if not args.no_hooks:
                print("[配置] 正在配置 conda 环境联动...")
                installer.install_conda_hooks()
                print("[完成] Conda 环境联动配置完成")
                conda_configured = True
            else:
                print("[提示] 跳过 conda 环境联动配置")
                conda_configured = False

            print("-" * 60)
            print("[说明] 安装位置: ~/.local/bin/uv")
            print("[说明] 配置文件: ~/.config/uv/uv.toml")
            print()
            print("[操作] 请执行以下命令启用 UV:")
            print("         source ~/.bashrc    # Bash 用户")
            print("         source ~/.zshrc     # Zsh 用户")
            print("         或重启终端")
            print()
            print("[验证] 安装完成后执行: uv --version")

            # conda 联动使用提示
            if not conda_configured:
                print()
                print("[可选] Conda 环境联动配置:")
                print("       如需让 UV 自动识别 conda 环境，请执行:")
                print("       fastuv install --hooks-only")
                print()
                print("[说明] Conda 环境联动作用:")
                print("       - 自动检测当前激活的 conda 环境")
                print("       - 在 conda 环境中使用 UV 管理包")
                print("       - 避免创建额外的 .venv 虚拟环境")

            print("=" * 60)
            return 0
        else:
            print("-" * 60)
            print("[错误] UV 安装失败")
            print("[建议] 请检查网络连接和权限设置")
            print("=" * 60)
            return 1

    except Exception as e:
        print("-" * 60)
        print(f"[错误] 安装过程中发生异常: {e}")
        print("[建议] 请查看详细错误信息并重试")
        print("=" * 60)
        return 1


def cmd_uninstall(args) -> int:
    """处理卸载命令"""
    try:
        uninstaller = UVUninstaller()

        print("=" * 60)
        print("fastuv - UV 卸载工具")
        print("=" * 60)

        if args.all:
            print("[模式] 完全卸载模式 - 将删除 UV 及所有配置文件")
        else:
            print("[模式] 基础卸载模式 - 仅删除 UV 二进制文件")

        print("-" * 60)

        success = uninstaller.uninstall(remove_all=args.all)

        if success:
            print("-" * 60)
            print("[完成] UV 卸载成功！")

            if args.all:
                print("[清理] 已清理以下项目:")
                print("       - UV 二进制文件 (~/.local/bin/uv)")
                print("       - UV 配置文件 (~/.config/uv/)")
                print("       - UV 缓存文件 (~/.cache/uv/)")
                print("       - Shell 配置中的 fastuv 相关设置")
            else:
                print("[说明] 仅删除了 UV 二进制文件")
                print("[保留] 配置文件和缓存保留，如需完全清理请使用 --all 参数")

            print()
            print("[建议] 请重启终端或执行以下命令:")
            print("         source ~/.bashrc    # Bash 用户")
            print("         source ~/.zshrc     # Zsh 用户")
            print("=" * 60)
            return 0
        else:
            print("-" * 60)
            print("[错误] UV 卸载失败")
            print("[建议] 请检查文件权限和进程占用")
            print("=" * 60)
            return 1

    except Exception as e:
        print("-" * 60)
        print(f"[错误] 卸载过程中发生异常: {e}")
        print("[建议] 请查看详细错误信息并重试")
        print("=" * 60)
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