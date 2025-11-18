# syntax=docker/dockerfile:1

# Build stage: Create the image with dependencies
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV

COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests

# Create venv and install dependencies
RUN uv venv "$VIRTUAL_ENV" && \
    uv pip install --no-cache -e .

FROM base AS dev

# Install git, sudo, ssh, make for development; ensure user with UID 1000 exists, set permissions and configure git
# apt-get required as we clean it up in the base image to publish smaller images
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    sudo \
    openssh-client \
    make \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean && \
    if id -u 1000 > /dev/null 2>&1; then \
    EXISTING_USER=$(id -un 1000) && \
    if [ "$EXISTING_USER" != "user" ]; then \
    usermod -l user -d /home/user -m "$EXISTING_USER" && \
    groupmod -n user $(id -gn 1000) 2>/dev/null || true; \
    fi; \
    else \
    groupadd --gid 1000 user && \
    useradd --create-home --no-log-init --gid 1000 --uid 1000 --shell /usr/bin/bash user; \
    fi && \
    chown -R 1000:1000 /opt/venv && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/nopasswd && \
    chmod 0440 /etc/sudoers.d/nopasswd && \
    usermod -aG sudo user && \
    git config --system --add safe.directory '*'

USER user

# Configure the shell for UID 1000
RUN mkdir -p ~/.history/ && \
    echo 'HISTFILE=~/.history/.bash_history' >> ~/.bashrc && \
    echo 'bind "\e[A": history-search-backward' >> ~/.bashrc && \
    echo 'bind "\e[B": history-search-forward' >> ~/.bashrc && \
    echo 'eval "$(starship init bash)"' >> ~/.bashrc
