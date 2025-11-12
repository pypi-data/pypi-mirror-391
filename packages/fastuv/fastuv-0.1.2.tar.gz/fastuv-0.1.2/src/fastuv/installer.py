"""
fastuv 安装器核心模块

负责下载、安装和配置 uv，包括镜像配置和环境设置
"""

import os
import sys
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional
import urllib.request
import json
import importlib.resources


class UVInstaller:
    """uv 安装器类"""

    def __init__(
        self,
        download_proxy: str = "https://ghfast.top",
        pypi_mirror: str = "https://pypi.tuna.tsinghua.edu.cn/simple/",
        version: Optional[str] = None
    ):
        self.download_proxy = download_proxy
        self.pypi_mirror = pypi_mirror
        self.version = version or "latest"
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()

        # 用户目录路径
        self.home_dir = Path.home()
        self.local_bin_dir = self.home_dir / ".local" / "bin"
        self.config_dir = self.home_dir / ".config" / "uv"

        # uv 相关路径
        self.uv_bin_path = self.local_bin_dir / "uv"
        self.uv_config_path = self.config_dir / "uv.toml"

    def get_latest_uv_version(self) -> str:
        """获取 uv 最新版本号"""
        try:
            url = "https://api.github.com/repos/astral-sh/uv/releases/latest"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return data["tag_name"].lstrip("v")
        except Exception:
            # 如果获取失败，返回默认版本
            return "0.5.0"

    def get_uv_download_url(self) -> str:
        """获取 uv 下载链接"""
        version = self.version if self.version != "latest" else self.get_latest_uv_version()

        # 确定平台和架构
        if self.platform == "linux":
            if self.arch in ["x86_64", "amd64"]:
                archive_name = f"uv-{version}-x86_64-unknown-linux-gnu.tar.gz"
            elif self.arch in ["aarch64", "arm64"]:
                archive_name = f"uv-{version}-aarch64-unknown-linux-gnu.tar.gz"
            else:
                raise RuntimeError(f"Unsupported architecture: {self.arch}")
        elif self.platform == "darwin":
            if self.arch in ["x86_64", "amd64"]:
                archive_name = f"uv-{version}-x86_64-apple-darwin.tar.gz"
            elif self.arch in ["aarch64", "arm64"]:
                archive_name = f"uv-{version}-aarch64-apple-darwin.tar.gz"
            else:
                raise RuntimeError(f"Unsupported architecture: {self.arch}")
        elif self.platform == "windows":
            if self.arch in ["x86_64", "amd64"]:
                archive_name = f"uv-{version}-x86_64-pc-windows-msvc.zip"
            elif self.arch in ["aarch64", "arm64"]:
                archive_name = f"uv-{version}-aarch64-pc-windows-msvc.zip"
            else:
                raise RuntimeError(f"Unsupported architecture: {self.arch}")
        else:
            raise RuntimeError(f"Unsupported platform: {self.platform}")

        # 使用代理下载
        base_url = f"{self.download_proxy}/https://github.com/astral-sh/uv/releases/download/{version}"
        return f"{base_url}/{archive_name}"

    def download_uv_installer_script(self) -> str:
        """下载官方 uv 安装脚本"""
        try:
            # 根据平台选择安装脚本
            if self.platform in ["linux", "darwin"]:
                script_url = "https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh"
                suffix = '.sh'
            elif self.platform == "windows":
                script_url = "https://github.com/astral-sh/uv/releases/latest/download/uv-installer.ps1"
                suffix = '.ps1'
            else:
                raise RuntimeError(f"Unsupported platform for installer script: {self.platform}")

            # 使用代理
            if self.platform == "windows":
                proxied_url = f"{self.download_proxy}/https://github.com/astral-sh/uv/releases/latest/download/uv-installer.ps1"
            else:
                proxied_url = f"{self.download_proxy}/https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh"

            # 下载脚本
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=suffix) as f:
                print("[下载] 正在下载 uv 安装脚本...")
                urllib.request.urlretrieve(proxied_url, f.name)
                return f.name

        except Exception as e:
            raise RuntimeError(f"下载 uv 安装脚本失败: {e}")

    def get_template_content(self, template_name: str) -> str:
        """获取包内模板文件内容"""
        try:
            if hasattr(importlib.resources, 'files'):
                # Python 3.9+
                return (importlib.resources.files('fastuv.templates') / template_name).read_text(encoding='utf-8')
            else:
                # Python 3.8
                with importlib.resources.path('fastuv.templates', template_name) as p:
                    return p.read_text(encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"无法读取模板文件 {template_name}: {e}")

    def get_hook_content(self, hook_name: str) -> str:
        """获取包内hook文件内容"""
        try:
            if hasattr(importlib.resources, 'files'):
                # Python 3.9+
                return (importlib.resources.files('fastuv.hooks') / hook_name).read_text(encoding='utf-8')
            else:
                # Python 3.8
                with importlib.resources.path('fastuv.hooks', hook_name) as p:
                    return p.read_text(encoding='utf-8')
        except Exception as e:
            raise RuntimeError(f"无法读取hook文件 {hook_name}: {e}")

    def create_custom_installer_script(self, original_script_path: str) -> str:
        """创建自定义安装脚本，注入镜像配置"""

        # 获取包内模板文件内容
        try:
            mirror_config_template = self.get_template_content('shell_injection.sh')
            # 替换模板中的占位符
            mirror_config = mirror_config_template.replace(
                '__DOWNLOAD_PROXY__', self.download_proxy
            ).replace(
                '__PYPI_MIRROR__', self.pypi_mirror
            )
        except Exception as e:
            # 如果无法读取模板文件，使用内置配置
            mirror_config = f'''
# --- fastuv 自定义配置：添加默认 PyPI 和 Python 下载镜像 ---
say "正在配置默认的 PyPI 和 Python 下载镜像..."
local _uv_config_dir="${{XDG_CONFIG_HOME:-$HOME/.config}}/uv"
ensure mkdir -p "$_uv_config_dir"
_UV_DOWNLOAD_PROXY_URL_FOR_CONFIG="${{UV_DOWNLOAD_PROXY:-{self.download_proxy}}}"
_UV_PYPI_MIRROR_URL="${{UV_PYPI_MIRROR:-{self.pypi_mirror}}}"
_UV_PYTHON_INSTALL_MIRROR_URL="${{_UV_DOWNLOAD_PROXY_URL_FOR_CONFIG}}/https://github.com/astral-sh/python-build-standalone/releases/download"
printf "python-install-mirror = \\"%s\\"\\\\n\\\\n[[index]]\\\\nurl = \\"%s\\"\\\\ndefault = true\\\\n" "$_UV_PYTHON_INSTALL_MIRROR_URL" "$_UV_PYPI_MIRROR_URL" > "$_uv_config_dir/uv.toml"
say "[完成] 配置完成。镜像设置如下:"
say "   - Python 下载代理: $_UV_DOWNLOAD_PROXY_URL_FOR_CONFIG"
say "   - PyPI 镜像源: $_UV_PYPI_MIRROR_URL"
say "   - 配置文件路径: $_uv_config_dir/uv.toml"
# --- fastuv 配置结束 ---
'''

        # 读取原始脚本
        with open(original_script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # 注入代理配置
        script_content = script_content.replace(
            'INSTALLER_BASE_URL="${UV_INSTALLER_GITHUB_BASE_URL:-https://github.com}"',
            f'INSTALLER_BASE_URL="${{UV_INSTALLER_GITHUB_BASE_URL:-{self.download_proxy}/https://github.com}}"'
        )

        # 在安装完成前注入镜像配置
        if 'say "everything\'s installed!"' in script_content:
            script_content = script_content.replace(
                'say "everything\'s installed!"',
                mirror_config + '\nsay "everything\'s installed!"'
            )

        # 创建自定义脚本
        custom_script_path = original_script_path.replace('.sh', '-custom.sh')
        with open(custom_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 设置执行权限
        os.chmod(custom_script_path, 0o755)

        return custom_script_path

    def ensure_local_bin_dir(self):
        """确保 ~/.local/bin 目录存在"""
        self.local_bin_dir.mkdir(parents=True, exist_ok=True)

    def update_path_in_shell(self):
        """更新 shell 配置文件中的 PATH"""
        shell_configs = [
            self.home_dir / ".bashrc",
            self.home_dir / ".zshrc",
            self.home_dir / ".profile"
        ]

        bin_path_str = str(self.local_bin_dir)
        path_entry = f'export PATH="{bin_path_str}:$PATH"'

        for config_file in shell_configs:
            if config_file.exists():
                content = config_file.read_text()
                if bin_path_str not in content:
                    with open(config_file, 'a') as f:
                        f.write(f"\n# fastuv: Add ~/.local/bin to PATH\n{path_entry}\n")

    def install(self) -> bool:
        """执行安装过程"""
        try:
            print(f"[信息] 目标平台: {self.platform}")
            print(f"[信息] uv 版本: {self.version}")

            # 1. 下载官方安装脚本
            script_path = self.download_uv_installer_script()

            try:
                # 2. 创建自定义安装脚本
                custom_script_path = self.create_custom_installer_script(script_path)

                # 3. 确保安装目录存在
                self.ensure_local_bin_dir()

                # 4. 执行安装
                print("[执行] 正在执行 uv 安装...")
                env = os.environ.copy()
                env.update({
                    "UV_DOWNLOAD_PROXY": self.download_proxy,
                    "UV_PYPI_MIRROR": self.pypi_mirror
                })

                if self.platform == "windows" and custom_script_path.endswith('.ps1'):
                    # Windows PowerShell
                    result = subprocess.run(
                        ["powershell", "-ExecutionPolicy", "Bypass", "-File", custom_script_path],
                        env=env,
                        capture_output=True,
                        text=True
                    )
                else:
                    # Linux/macOS shell
                    result = subprocess.run(
                        [custom_script_path],
                        env=env,
                        capture_output=True,
                        text=True
                    )

                if result.returncode != 0:
                    print(f"[错误] 安装失败: {result.stderr}")
                    return False

                # 5. 更新 PATH
                self.update_path_in_shell()

                return True

            finally:
                # 清理临时文件
                for path in [script_path, custom_script_path]:
                    if os.path.exists(path):
                        os.unlink(path)

        except Exception as e:
            print(f"[错误] 安装过程中发生错误: {e}")
            return False

    def install_conda_hooks(self):
        """安装 conda 环境联动 hooks"""
        try:
            print("[配置] 正在配置 conda 环境联动...")

            # 获取包内 conda hook 内容
            try:
                conda_hook = self.get_hook_content('conda_env.sh')
            except Exception:
                # 如果无法读取模板文件，使用内置配置
                conda_hook = '''
# fastuv conda 环境联动
_sync_fastuv_conda_env() {
  if [ -n "$CONDA_PREFIX" ]; then
    if [ -z "$UV_PROJECT_ENVIRONMENT" ] || [ "$UV_PROJECT_ENVIRONMENT" != "$CONDA_PREFIX" ]; then
      export UV_PROJECT_ENVIRONMENT="$CONDA_PREFIX"
    fi
  else
    if [ -n "$UV_PROJECT_ENVIRONMENT" ]; then
      unset UV_PROJECT_ENVIRONMENT
    fi
  fi
}

# Bash
if [[ -n "$BASH_VERSION" && ! "$PROMPT_COMMAND" =~ _sync_fastuv_conda_env ]]; then
  PROMPT_COMMAND="_sync_fastuv_conda_env;$PROMPT_COMMAND"
fi

# Zsh
if [[ -n "$ZSH_VERSION" && ! " ${precmd_functions[@]} " =~ " _sync_fastuv_conda_env " ]]; then
  precmd_functions+=(_sync_fastuv_conda_env)
fi
'''

            # 写入到 shell 配置文件
            shell_configs = [
                self.home_dir / ".bashrc",
                self.home_dir / ".zshrc"
            ]

            for config_file in shell_configs:
                if config_file.exists():
                    content = config_file.read_text()
                    if "_sync_fastuv_conda_env" not in content:
                        with open(config_file, 'a') as f:
                            f.write(conda_hook)

            print("[完成] conda 环境联动配置完成")

        except Exception as e:
            print(f"[警告] 配置 conda 环境联动失败: {e}")
            # 不影响主安装流程