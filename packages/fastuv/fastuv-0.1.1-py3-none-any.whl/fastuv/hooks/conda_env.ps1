# fastuv conda 环境联动脚本 (PowerShell)
# 此脚本将被注入到用户的 PowerShell 配置文件中

# Auto-sync UV_PROJECT_ENVIRONMENT with Conda/Mamba environment (PowerShell).
# This function is registered to run before each prompt is displayed.
Register-EngineEvent -SourceIdentifier PowerShell.OnIdle -Action {
    if (Test-Path Env:CONDA_PREFIX) {
        if (-not (Test-Path Env:UV_PROJECT_ENVIRONMENT) -or ($env:UV_PROJECT_ENVIRONMENT -ne $env:CONDA_PREFIX)) {
            $env:UV_PROJECT_ENVIRONMENT = $env:CONDA_PREFIX
        }
    } else {
        if (Test-Path Env:UV_PROJECT_ENVIRONMENT) {
            Remove-Item -ErrorAction SilentlyContinue Env:UV_PROJECT_ENVIRONMENT
        }
    }
}