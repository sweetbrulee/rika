FROM python:3.12-bookworm 

# 设置环境变量，确保 Python 输出不缓冲
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends ffmpeg libopus0 git curl lsof && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /workspace/rika

# 复制应用代码
COPY . .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.dev.txt


