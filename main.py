import subprocess
import sys
import time
import threading

def read_stderr(process, script, error_list, critical_error_list):
    """讀取子進程的 stderr，記錄錯誤訊息，區分致命與非致命錯誤"""
    try:
        for line in iter(process.stderr.readline, ''):
            line = line.strip()
            if "CRITICAL" in line or "fatal" in line or "FATAL" in line:
                critical_error_list.append(f"[{script}] 💥 致命錯誤: {line}")
            elif "ERROR" in line or "Error" in line or "Exception" in line:
                error_list.append(f"[{script}] ❌ 錯誤: {line}")
    except ValueError:
        # 當 process.stderr 被關閉後可能會引發 ValueError，這裡捕捉後就結束
        pass

def main():
    scripts = ["chat.py", "boss.py", "food.py", "material.py", "invite.py"]
    processes = []
    error_logs = []
    critical_error_logs = []
    stderr_threads = []  # 記錄所有讀取 stderr 的線程

    print("🔄 登入中...")  # 登入中訊息

    # 啟動所有目標檔案，同時在同一行印出「正在載入: 檔名...」
    for script in scripts:
        print(f"正在載入: {script}...", end=" ", flush=True)
        process = subprocess.Popen(
            ["python", script],
            stdout=subprocess.DEVNULL,  # 隱藏標準輸出
            stderr=subprocess.PIPE,       # 捕獲錯誤輸出
            text=True,
            bufsize=1                   # 讓錯誤日誌即時刷新
        )
        processes.append((script, process))
        # 啟動線程即時讀取該進程的 stderr
        thread = threading.Thread(target=read_stderr, args=(process, script, error_logs, critical_error_logs), daemon=True)
        thread.start()
        stderr_threads.append(thread)

    # 輸出完所有正在載入的訊息後換行
    print()

    # 將等待時間從 3 秒縮短至 0.5 秒
    time.sleep(0.5)

    # 檢查每個子進程是否仍在運行，並換行顯示對應的狀態
    for script, process in processes:
        if process.poll() is None:
            print(f"✅ {script} 載入成功")
        else:
            print(f"❌ {script} 載入失敗")
            critical_error_logs.append(f"{script} 未能成功啟動")

    # 等待所有 stderr 線程結束（設置短暫 timeout 以免阻塞）
    for thread in stderr_threads:
        thread.join(timeout=1)

    # 如果有致命錯誤，則報告後退出程式
    if critical_error_logs:
        print("\n❗ 發現致命錯誤，無法登入：")
        for err in critical_error_logs:
            print(err)
        print("❌ 測試醬 無法登入.")
        sys.exit(1)

    # 全部檔案載入成功後，顯示登入成功訊息
    print("✅ 女僕月醬 已登入.")

    # 如果有非致命錯誤，則報告（但不影響登入成功）
    if error_logs:
        print("\n⚠️ 載入過程中發現錯誤，但不影響登入：")
        for err in error_logs:
            print(err)

if __name__ == "__main__":
    main()
