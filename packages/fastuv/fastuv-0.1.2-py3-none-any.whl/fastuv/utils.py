"""
fastuv 工具模块

提供通用的工具函数
"""

import os
import sys
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


def detect_platform() -> Dict[str, str]:
    """检测平台信息"""
    return {
        "system": platform.system().lower(),
        "machine": platform.machine().lower(),
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }


def detect_shell() -> Optional[str]:
    """检测当前使用的 shell"""
    shell = os.environ.get("SHELL", "")
    if "bash" in shell:
        return "bash"
    elif "zsh" in shell:
        return "zsh"
    elif "fish" in shell:
        return "fish"
    else:
        return None


def get_user_config_dir() -> Path:
    """获取用户配置目录"""
    if platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        return Path.home() / ".config"


def get_user_data_dir() -> Path:
    """获取用户数据目录"""
    if platform.system() == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        return Path.home() / ".local" / "share"


def get_user_cache_dir() -> Path:
    """获取用户缓存目录"""
    if platform.system() == "Windows":
        return Path(os.environ.get("TEMP", tempfile.gettempdir()))
    else:
        return Path.home() / ".cache"


def ensure_directory(path: Path) -> bool:
    """确保目录存在"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def is_command_available(command: str) -> bool:
    """检查命令是否可用"""
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_command(
    command: list,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """运行命令"""
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return e


def download_file(url: str, dest: Path) -> bool:
    """下载文件"""
    try:
        import urllib.request
        urllib.request.urlretrieve(url, dest)
        return True
    except Exception:
        return False


def read_file_safe(path: Path) -> Optional[str]:
    """安全读取文件"""
    try:
        if path.exists():
            return path.read_text(encoding='utf-8')
        return None
    except Exception:
        return None


def write_file_safe(path: Path, content: str) -> bool:
    """安全写入文件"""
    try:
        ensure_directory(path.parent)
        path.write_text(content, encoding='utf-8')
        return True
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def print_success(message: str):
    """打印成功消息"""
    print(f"[完成] {message}")


def print_error(message: str):
    """打印错误消息"""
    print(f"[错误] {message}")


def print_warning(message: str):
    """打印警告消息"""
    print(f"[警告] {message}")


def print_info(message: str):
    """打印信息消息"""
    print(f"[信息] {message}")


def confirm(message: str, default: bool = False) -> bool:
    """用户确认"""
    suffix = " [Y/n]" if default else " [y/N]"

    try:
        response = input(f"{message}{suffix}: ").strip().lower()

        if not response:
            return default

        return response in ["y", "yes", "是", "确认"]
    except (KeyboardInterrupt, EOFError):
        return False