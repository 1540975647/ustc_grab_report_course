#!/bin/bash
# === 配置区 ===
PYTHON="/usr/bin/python3"
MAIN_PY="/root/ustc_grab_report_course/main.py"
UPDATE_PY="/root/ustc_grab_report_course/main_update_weu.py"

BASE_LOG_DIR="/var/log/ustc_grab"
MAIN_LOG_DIR="$BASE_LOG_DIR/main"
UPDATE_LOG_DIR="$BASE_LOG_DIR/update"
ERR_LOG_DIR="$BASE_LOG_DIR/error"

MAX_SIZE_MB=100  # 每个子目录最大允许大小

mkdir -p "$MAIN_LOG_DIR" "$UPDATE_LOG_DIR" "$ERR_LOG_DIR"

# 检查 Python 路径
if [ ! -x "$PYTHON" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Python not found at $PYTHON" >> "$ERR_LOG_DIR/init_error.txt"
    exit 1
fi

# 捕获退出信号
trap 'echo "[$(date "+%Y-%m-%d %H:%M:%S")] Script stopped by user" >> "$ERR_LOG_DIR/$(date "+%Y-%m-%d_stop.txt")"; exit 0' SIGINT SIGTERM

# === 清理函数 ===
cleanup_logs() {
    local dir="$1"
    local total_kb
    total_kb=$(du -sk "$dir" | awk '{print $1}')
    local total_mb=$((total_kb / 1024))

    if (( total_mb > MAX_SIZE_MB )); then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleaning $dir (current: ${total_mb}MB)" >> "$ERR_LOG_DIR/cleanup.log"
        # 删除最老的文件直到低于限制
        while (( total_mb > MAX_SIZE_MB )); do
            oldest=$(ls -1t "$dir" | tail -n 1)
            [ -n "$oldest" ] && rm -f "$dir/$oldest"
            total_kb=$(du -sk "$dir" | awk '{print $1}')
            total_mb=$((total_kb / 1024))
        done
    fi
}

minute_counter=0

# === 主循环 ===
while true; do
    start_sec=$(date +%s)
    timestamp=$(date '+%Y-%m-%d_%H-%M-%S')

    MAIN_LOG="$MAIN_LOG_DIR/$timestamp.txt"
    ERR_LOG="$ERR_LOG_DIR/$timestamp.txt"

    # 每分钟执行一次 main.py
    "$PYTHON" "$MAIN_PY" >> "$MAIN_LOG" 2>>"$ERR_LOG"

    # 每30分钟执行一次 main_update_weu.py
    if (( minute_counter == 0 )); then
        UPDATE_LOG="$UPDATE_LOG_DIR/$timestamp.txt"
        "$PYTHON" "$UPDATE_PY" >> "$UPDATE_LOG" 2>>"$ERR_LOG"
        cleanup_logs "$UPDATE_LOG_DIR"
    fi

    # 每轮执行完清理日志目录（主与错误）
    cleanup_logs "$MAIN_LOG_DIR"
    cleanup_logs "$ERR_LOG_DIR"

    ((minute_counter = (minute_counter + 1) % 30))

    # 精确控制时间
    end_sec=$(date +%s)
    elapsed=$((end_sec - start_sec))
    sleep_sec=$((60 - elapsed))

    if (( sleep_sec > 0 )); then
        # 正常等待补齐一分钟
        sleep "$sleep_sec"
    elif (( sleep_sec < -120 )); then
        # 任务超出两分钟以上，认为异常
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Warning: Task took ${elapsed}s, exceeded expected 60s." >> "$ERR_LOG"
        sleep 1
    else
        # 小范围延迟（例如 Python 内部随机延时），忽略警告
        sleep 1
    fi

done
