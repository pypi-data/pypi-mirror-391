# 第一阶段：使用带 uv 的镜像构建依赖
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 仅安装依赖（不含项目代码）
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# 添加源码并安装项目本身
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable


# 第二阶段：轻量运行时
FROM python:3.12-slim-bookworm

WORKDIR /app
 
COPY --from=uv /root/.local /root/.local
COPY --from=uv --chown=app:app /app/.venv /app/.venv


# 将 venv 加入 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 可选：挂载数据库的默认目录
VOLUME ["/home/app/data"]

ENV LOCAL_NAME=${LOCAL_NAME:-"啵啵"}

# 启动你的 MCP 服务器
ENTRYPOINT ["mcp_server_nbotbb", "--local-name", "${LOCAL_NAME}"]


