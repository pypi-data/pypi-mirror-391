"""
fastuv 卸载器模块

负责卸载 uv 和清理相关配置文件
"""

import os
import shutil
from pathlib import Path
from typing import List


class UVUninstaller:
    """uv 卸载器类"""

    def __init__(self):
        self.home_dir = Path.home()
        self.local_bin_dir = self.home_dir / ".local" / "bin"
        self.config_dir = self.home_dir / ".config" / "uv"
        self.cache_dir = self.home_dir / ".cache" / "uv"

        # uv 相关路径
        self.uv_bin_path = self.local_bin_dir / "uv"
        self.uv_config_path = self.config_dir / "uv.toml"

    def get_shell_config_files(self) -> List[Path]:
        """获取 shell 配置文件列表"""
        return [
            self.home_dir / ".bashrc",
            self.home_dir / ".bash_profile",
            self.home_dir / ".zshrc",
            self.home_dir / ".profile",
            self.home_dir / ".config/fish/config.fish"
        ]

    def remove_fastuv_from_shell_configs(self):
        """从 shell 配置文件中移除 fastuv 相关配置"""
        shell_configs = self.get_shell_config_files()

        markers = [
            "# fastuv:",
            "# fastuv conda 环境联动",
            "_sync_fastuv_conda_env",
            "UV_PROJECT_ENVIRONMENT"
        ]

        for config_file in shell_configs:
            if not config_file.exists():
                continue

            try:
                # 读取文件内容
                lines = config_file.read_text(encoding='utf-8').split('\n')

                # 过滤掉包含 fastuv 相关标记的行
                filtered_lines = []
                skip_line = False

                for i, line in enumerate(lines):
                    # 检查是否应该跳过这行
                    should_skip = any(marker in line for marker in markers)

                    if should_skip:
                        skip_line = True
                        continue

                    # 如果之前在跳过，并且这行是空的，可能跳过整个块
                    if skip_line and line.strip() == "":
                        skip_line = False
                        continue

                    if not skip_line:
                        filtered_lines.append(line)

                # 写回文件
                config_file.write_text('\n'.join(filtered_lines), encoding='utf-8')
                print(f"[配置] 已清理 shell 配置: {config_file.name}")

            except Exception as e:
                print(f"[警告] 清理 shell 配置失败: {config_file.name} ({e})")

    def remove_uv_binary(self):
        """移除 uv 二进制文件"""
        if self.uv_bin_path.exists():
            try:
                self.uv_bin_path.unlink()
                print(f"[删除] 已删除 UV 二进制文件: {self.uv_bin_path.name}")
            except Exception as e:
                print(f"[警告] 删除 UV 二进制文件失败 ({e})")
        else:
            print("[信息] UV 二进制文件不存在")

    def remove_uv_config(self):
        """移除 uv 配置文件"""
        if self.config_dir.exists():
            try:
                shutil.rmtree(self.config_dir)
                print(f"[删除] 已删除 UV 配置目录: {self.config_dir.name}")
            except Exception as e:
                print(f"[警告] 删除 UV 配置目录失败 ({e})")
        else:
            print("[信息] UV 配置目录不存在")

    def remove_uv_cache(self):
        """移除 uv 缓存"""
        if self.cache_dir.exists():
            try:
                shutil.rmtree(self.cache_dir)
                print(f"[删除] 已删除 UV 缓存目录: {self.cache_dir.name}")
            except Exception as e:
                print(f"[警告] 删除 UV 缓存目录失败 ({e})")
        else:
            print("[信息] UV 缓存目录不存在")

    def check_uv_installation(self) -> bool:
        """检查 uv 是否已安装"""
        return self.uv_bin_path.exists() or self.config_dir.exists()

    def uninstall(self, remove_all: bool = False) -> bool:
        """执行卸载过程"""
        try:
            print("[开始] 开始卸载 uv...")

            if not self.check_uv_installation():
                print("[信息] 未检测到 uv 安装")
                return True

            # 1. 移除 uv 二进制文件
            self.remove_uv_binary()

            # 2. 移除配置文件
            self.remove_uv_config()

            # 3. 清理 shell 配置中的 fastuv 设置
            print("[清理] 正在清理 shell 配置...")
            self.remove_fastuv_from_shell_configs()

            # 4. 可选：清理缓存
            if remove_all:
                print("[清理] 正在清理缓存文件...")
                self.remove_uv_cache()

            print("[完成] uv 卸载完成！")
            print("[提示] 请重启终端或运行 'source ~/.bashrc' 以应用更改")

            return True

        except Exception as e:
            print(f"[错误] 卸载过程中发生错误: {e}")
            return False