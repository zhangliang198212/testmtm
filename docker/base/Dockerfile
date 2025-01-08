ARG GOLANG_VERSION=${GOLANG_VERSION:-"1.23.3"}
ARG WORK_DIR=${WORK_DIR:-"/app"}
ARG NONROOT_USER=${NONROOT_USER:-"user"}
ARG PYTHON_VERSION=${PYTHON_VERSION:-"3.13"}
ARG NODE_VERSION=${NODE_VERSION:-"20.18.1"}
ARG DEFAULT_PASSWORD=${DEFAULT_PASSWORD:-"Admin123!@"}

FROM debian AS base
ARG NONROOT_USER=${NONROOT_USER:-"user"}

ENV BUILD_STAGE=true
ENV PATH=/app/bin:/app/hack:/app/hack/dev:/app/hack:${HOME}/.local/bin:$PATH
ENV SHELL=/bin/bash

RUN apt update -yqq --fix-missing && apt -yqq --no-install-recommends install \
    sudo git curl wget ca-certificates gnupg2 unzip lsb-release \
    iptables iproute2 net-tools inetutils-ping dnsutils \
    ncat socat \
    openssh-server \
    make \
    cmake \
    gettext-base \
    libpcap-dev \
    make build-essential libssl-dev \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* && rm -rf /var/lib/apt/lists/*


RUN apt update -yqq --fix-missing && apt -yqq --no-install-recommends install \
    zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
    llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* && rm -rf /var/lib/apt/lists/*


#############################
# 安装 Go
ARG GOLANG_VERSION=${GOLANG_VERSION:-"1.23.3"}
ENV GOLANG_VERSION=${GOLANG_VERSION}
ENV GOPATH=/usr/local/go
ENV PATH=$GOPATH/bin:$PATH
RUN curl -o /tmp/goinstall.tar.gz -sSL https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf /tmp/goinstall.tar.gz \
    && rm /tmp/goinstall.tar.gz
RUN echo 'export PATH="$GOPATH/bin:$PATH"' >> /etc/profile

# 如果使用uv 作为主要的 python 运行时,则需要确保 rust 正确安装,因为类似 tiktoken 这样的包安装是,需要编译,编译过程需要 rust.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

#############################
# python



ENV UV_TOOL_BIN_DIR=/opt/uv-bin/
RUN command -v uv ||  curl -LsSf https://astral.sh/uv/install.sh | sudo sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"
ENV PATH="${UV_TOOL_BIN_DIR}/:$PATH"
RUN uv version
# 自动安装最新版
# RUN uv python install
RUN uv python install 3.12
RUN uv version
# Create virtual environment and install packages
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Create symlinks before using uv
RUN ln -sf $(which python3) /usr/local/bin/python && ln -sf $(which pip3) /usr/local/bin/pip
RUN uv pip install --no-cache-dir -U wheel setuptools uvicorn poetry hatch
# 安装 python 依赖
RUN apt update -yqq --fix-missing && apt -yqq --no-install-recommends install \
    cmake \
    gcc \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    sentencepiece \
    libsentencepiece-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    pkg-config \
    libgoogle-perftools-dev \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* && rm -rf /var/lib/apt/lists/*

#############################
# nodejs
# nvm environment variables
ENV NVM_DIR=/usr/local/nvm
ENV NODE_VERSION=${NODE_VERSION:-"20.18.1"}
RUN mkdir -p $NVM_DIR \
    && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default
# RUN source "${NVM_DIR}/nvm.sh" && nvm install --lts
# ENV PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}/bin:${PATH}"
# add node and npm to path so the commands are available
ENV NODE_PATH=$NVM_DIR/v$NODE_VERSION/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH
# /usr/local/nvm/versions/node/v20.18.1/bin/npm
RUN echo "export NVM_DIR=$NVM_DIR" >> ${HOME}/.bashrc \
    && echo "export NODE_VERSION=$NODE_VERSION" >> ${HOME}/.bashrc \
    && echo 'export PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"' >> ${HOME}/.bashrc

RUN echo 'Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/bin/npm"' >> /etc/sudoers


RUN npm install -g pnpm yarn

# bun
ENV BUN_INSTALL="/.bun"
ENV PATH="$BUN_INSTALL/bin:$PATH"
RUN curl -fsSL https://bun.sh/install | bash
RUN echo "export BUN_INSTALL=$BUN_INSTALL" >> ${HOME}/.bashrc \
    && echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ${HOME}/.bashrc

# cloudflared
RUN curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    && sudo dpkg -i cloudflared.deb \
    && rm cloudflared.deb

RUN curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --yes --dearmor --output /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list \
    && sudo apt-get update && sudo apt-get install -yqq cloudflare-warp \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.gpg | sudo apt-key add - \
    && curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.list | sudo tee /etc/apt/sources.list.d/tailscale.list \
    && apt-get update -yqq && apt-get install -y tailscale \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*


# postgresql
RUN sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - \
    && apt-get update && apt-get install -yqq --no-install-recommends postgresql-16 postgresql-16-pgvector \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* && rm -rf /var/lib/apt/lists/*




WORKDIR ${WORK_DIR}

# COPY Taskfile.yaml ${WORK_DIR}/Taskfile.yaml
# COPY ./hack ${WORK_DIR}/hack
# COPY mtm/embed/bin ${WORK_DIR}/bin
# COPY bin/garagemq ${WORK_DIR}/bin/garagemq

RUN bash ${WORK_DIR}/hack/dev/pkg.sh install

RUN useradd --user-group --create-home --no-log-init --shell /bin/bash ${NONROOT_USER}
RUN usermod -aG sudo ${NONROOT_USER}
RUN echo "${NONROOT_USER} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# RUN bash ${WORK_DIR}/hack/dev/install_py install

# RUN bash ${WORK_DIR}/hack/dev/pkg.sh install_nodejs

# RUN node -v &&  npm -v && bun -v && pnpm -v

# RUN GOLANG_VERSION=${GOLANG_VERSION} bash ${WORK_DIR}/hack/dev/install-golang.sh install

# RUN bash ${WORK_DIR}/hack/dev/vnc install

# RUN bash ${WORK_DIR}/hack/dev/pkg.sh playwright

# CMD ["dockerentry"]




# ================================================================================================================================================
FROM kalilinux/kali-rolling:latest AS build_base
ENV W_DIR=${BASE_DIR:-/app}
ENV DEBIAN_FRONTEND=noninteractive
ENV IS_DOCKER_BUILD=1
ENV PNPM_HOME=/pnpm
WORKDIR ${W_DIR}
RUN apt update -q --fix-missing && apt -y install \
    sudo curl unzip git \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*

RUN  curl -fsSL https://bun.sh/install | bash -

ENV BUN_INSTALL="/root/.bun"
ENV PATH=$BUN_INSTALL/bin:${PATH}


# nvm
ENV NVM_DIR="/root/.nvm"
RUN curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# nvm install 20 && nvm alias default 20
# python base
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends --fix-missing -y \
    python python-pip python3-venv python3-distutils \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*


# golang ----------------------------------------------------------------------------------------------------------
# COPY bin/library-scripts/go-debian.sh /tmp/library-scripts/
# ENV INSTALL_GO_TOOLS=false
# RUN apt-get update && bash /tmp/library-scripts/go-debian.sh

# ----------------------------------------------------------------------------------------------------------------
#
FROM build_base AS builder_mtm
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine
# to understand why libc6-compat might be needed.
WORKDIR /app
RUN apt-get update && apt-get install -y  curl \
    git \
    mercurial \
    make \
    binutils \
    bison \
    gcc \
    build-essential
ARG TRPC_BACKEND
ENV TRPC_BACKEND=${TRPC_BACKEND}
ENV NEXT_TELEMETRY_DISABLED=1
ENV BUILD_MODE="standalone"
ENV IN_DOCKER_BUILD=TRUE

ENV GOPATH=/root/go
ENV PATH=$PATH:$GOPATH/bin:/usr/local/go/bin:${PATH}
# 安装 Go
ENV GVM_VERSION=master
# RUN curl -o go${GOLANG_VERSION}.linux-amd64.tar.gz -L https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz \
#     && tar -C /usr/local -xzf go${GOLANG_VERSION}.linux-amd64.tar.gz \
#     && rm go${GOLANG_VERSION}.linux-amd64.tar.gz
# # 获取 GOPATH 值并设置 PATH
# RUN echo 'export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"' >> /etc/profile \
#     && echo 'export GOPATH=/root/go' >> /root/.bashrc \
#     && echo 'export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"' >> /root/.bashrc
COPY ./go.mod ./go.mod
COPY ./go.sum ./go.sum
RUN go mod tidy
COPY . .

RUN CGO_ENABLED=1 GOOS=linux go build -ldflags="-s -w" -o dist/gomtm cmd/main.go


# -------------------------------------------------------------------------------------------------------------
# 开发环境
ARG BASE_DIR="/app"
# ------------------------------------------------------------------------------------
# 基本软件环境
FROM kalilinux/kali-rolling:latest AS dep
ENV W_DIR=${BASE_DIR:-/app}
ENV DEBIAN_FRONTEND=noninteractive
ENV IS_DOCKER_BUILD=1
ENV PNPM_HOME=/pnpm
WORKDIR ${W_DIR}

# --no-install-recommends
RUN apt update -q --fix-missing && apt -y install \
    sudo \
    cmake \
    gnupg2 \
    git \
    unzip \
    iptables \
    iproute2 \
    net-tools \
    inetutils-ping \
    curl \
    wget \
    ncat \
    socat \
    dnsutils \
    openssh-server \
    make \
    gettext-base \
    sudo \
    libpcap-dev \
    && apt -y autoremove && apt-get -y clean && rm -rf /tmp/* \
    && rm -rf /var/lib/apt/lists/*


COPY buildtool/* /usr/bin/
COPY buildtool/install ./bin/install
COPY docker/install_scripts/docker.sh /tmp/
RUN /tmp/docker.sh
# ￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥
##
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="false"
COPY docker/bin/* /usr/bin/
RUN chmod +x /usr/bin/*

# cloudflared
RUN curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
    && sudo dpkg -i cloudflared.deb \
    && rm cloudflared.deb

ENV GOLANG_VERSION=${GOLANG_VERSION:-"1.22"}
# 设置Go Path
# ENV GOPATH=/usr/local/go
ENV GOPATH=/root/go
ENV PATH=$PATH:$GOPATH/bin:/usr/local/go/bin:${PATH}
# 安装 Go
RUN curl -o go${GOLANG_VERSION}.linux-amd64.tar.gz -L https://go.dev/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GOLANG_VERSION}.linux-amd64.tar.gz \
    && rm go${GOLANG_VERSION}.linux-amd64.tar.gz
# 获取 GOPATH 值并设置 PATH
RUN echo 'export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"' >> /etc/profile \
    && echo 'export GOPATH=/root/go' >> /root/.bashrc \
    && echo 'export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"' >> /root/.bashrc


#----------------------------------------------------------------------------------------------------------------
# 基本的开发环境
FROM dep AS dev
ENV W_DIR=${BASE_DIR:-/app}
WORKDIR ${W_DIR}

RUN apt install -y postgresql-client-16


COPY bin/install_scripts/docker.sh /tmp/
RUN /tmp/docker.sh

COPY ./bin/container_bin/* /usr/bin/
COPY bin/install_scripts/docker.sh /tmp/
RUN /tmp/docker.sh
##  vscode
RUN curl -o 1.deb https://vscode.download.prss.microsoft.com/dbazure/download/stable/0ee08df0cf4527e40edc9aa28f4b5bd38bbff2b2/code_1.85.1-1702462158_amd64.deb \
    && sudo dpkg -i 1.deb && sudo rm 1.deb

RUN apt update && apt install -y dbus-x11 \
    x11-utils \
    x11-xserver-utils \
    xdg-utils

