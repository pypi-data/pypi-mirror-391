# fastuv conda 环境联动脚本
# 此脚本将被注入到用户的 shell 配置文件中

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

# Bash 环境联动
if [[ -n "$BASH_VERSION" && ! "$PROMPT_COMMAND" =~ _sync_fastuv_conda_env ]]; then
  PROMPT_COMMAND="_sync_fastuv_conda_env;$PROMPT_COMMAND"
fi

# Zsh 环境联动
if [[ -n "$ZSH_VERSION" && ! " ${precmd_functions[@]} " =~ " _sync_fastuv_conda_env " ]]; then
  precmd_functions+=(_sync_fastuv_conda_env)
fi