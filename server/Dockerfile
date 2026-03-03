# ============================================================
# rAthena Docker Image — 針對 Synology NAS 部署優化
# 在 macOS 上以 docker buildx 建置 linux/amd64 映像
# ============================================================

# ------ Stage 1: 編譯 rAthena ------
FROM --platform=linux/amd64 ubuntu:22.04 AS builder

ARG RATHENA_BRANCH=master
ARG PACKETVER=20220406
ARG BUILD_MODE=re

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git make gcc g++ \
    libmariadb-dev libmariadb-dev-compat \
    zlib1g-dev libpcre3-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 下載 rAthena 原始碼
# RATHENA_COMMIT: 釘定穩定 commit（空字串 = 用 RATHENA_BRANCH 最新版）
# CACHEBUST: 強制重新 clone，傳 $(date +%s) 即可
ARG RATHENA_COMMIT=""
ARG CACHEBUST=1
RUN git clone --branch ${RATHENA_BRANCH} \
    https://github.com/rathena/rathena.git /build/rathena \
    && if [ -n "${RATHENA_COMMIT}" ]; then \
        git -C /build/rathena checkout ${RATHENA_COMMIT}; \
    fi

WORKDIR /build/rathena

# 根據 BUILD_MODE 選擇 Pre-Renewal 或 Renewal
RUN if [ "${BUILD_MODE}" = "pre-re" ]; then \
        ./configure --enable-packetver=${PACKETVER} --enable-prere; \
    else \
        ./configure --enable-packetver=${PACKETVER}; \
    fi \
    && echo '#undef PACKET_OBFUSCATION' >> src/custom/defines_post.hpp \
    && make clean && make server -j$(nproc)

# 確保 log 目錄存在 & 確認編譯成功
RUN mkdir -p log && ls -la login-server char-server map-server


# ------ Stage 2: 精簡運行映像 ------
FROM --platform=linux/amd64 ubuntu:22.04 AS runtime

LABEL maintainer="RO NAS Server"
LABEL description="rAthena Ragnarok Online server for Synology NAS"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Taipei

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 libpcre3 zlib1g \
    default-mysql-client \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 從 builder 複製編譯好的檔案
WORKDIR /rathena
COPY --from=builder /build/rathena/login-server .
COPY --from=builder /build/rathena/char-server .
COPY --from=builder /build/rathena/map-server .

# 複製設定檔與遊戲資料（從本地 repo，已釘定 rAthena commit f464a8b）
COPY conf/ ./conf/
COPY db/ ./db/
COPY npc/ ./npc/
COPY sql-files/ ./sql-files/
RUN mkdir -p log

# 複製啟動腳本
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chmod +x login-server char-server map-server

# 對外 Port
EXPOSE 6900 6121 5121

# 環境變數（可在 docker-compose.yml 中覆蓋）
ENV DB_HOST=db \
    DB_PORT=3306 \
    DB_USER=ragnarok \
    DB_PASS=ragnarok \
    DB_NAME=ragnarok \
    SERVER_NAME=MyRO \
    CHAR_PUBLIC_IP=127.0.0.1 \
    MAP_PUBLIC_IP=127.0.0.1 \
    BASE_EXP_RATE=500 \
    JOB_EXP_RATE=500 \
    DROP_RATE=300 \
    CARD_DROP_RATE=1000

ENTRYPOINT ["/entrypoint.sh"]
