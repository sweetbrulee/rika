# -----------------------------------
# 构建阶段
# -----------------------------------
FROM python:3.12-slim-bookworm AS builder

# 安装系统依赖
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /home/user/rika

# 复制 requirements.txt
COPY requirements.txt .

# 创建虚拟环境
RUN python3 -m venv .venv

# 在虚拟环境中安装 Python 依赖
RUN .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install --no-cache-dir wheel && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt

# -----------------------------------
# 运行阶段
# -----------------------------------
FROM python:3.12-slim-bookworm AS runner

# 安装运行时依赖（如 ffmpeg）
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends ffmpeg libopus0 && \
    # apt-get install -y --no-install-recommends vim curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    # 创建一个非 root 用户
    useradd --create-home user

# 切换到非 root 用户
USER user

# 创建应用目录
RUN mkdir /home/user/rika

# 从 builder 阶段复制虚拟环境
COPY --from=builder /home/user/rika/.venv /home/user/rika/.venv

# 设置工作目录
WORKDIR /home/user/rika

# 复制应用代码
COPY . .

# 设置环境变量以使用虚拟环境
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/home/user/rika/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# 执行启动脚本
CMD [".", "script/run.sh"]