import subprocess
import sys
import time
import threading
from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# 全域字典用來存放各個腳本的錯誤訊息
error_logs = {}

def read_stderr(script, process):
    """
    從 process 的 stderr 中讀取每行訊息，並存入 error_logs 中。
    如果訊息中包含不希望顯示的內容，則直接略過。
    """
    skip_message = "[INFO    ] discord.client: logging in using static token"
    for line in iter(process.stderr.readline, ''):
        line = line.strip()
        if line:
            if skip_message in line:
                continue
            error_logs.setdefault(script, []).append(line)

def main():
    # 要啟動的腳本列表
    scripts = ["chat.py", "boss.py", "food.py", "material.py", "invite.py", "update.py", "help.py", "exp_calc.py", "discord-openai.py", "galgame1.py"]
    processes = []
    threads = []

    print("🔄 登入中...")

    # 逐一啟動各個腳本，並用線程讀取 stderr（錯誤輸出）
    for script in scripts:
        print(f"正在載入: {script}...", end=" ", flush=True)
        proc = subprocess.Popen(
            ["python", script, "--remove-help"],  # 參數可傳給其他腳本，但 help.py 已直接用 help_command=None
            stdout=subprocess.DEVNULL,   # 隱藏標準輸出
            stderr=subprocess.PIPE,        # 捕獲錯誤輸出
            bufsize=1,
            text=True
        )
        processes.append((script, proc))
        thread = threading.Thread(target=read_stderr, args=(script, proc), daemon=True)
        thread.start()
        threads.append(thread)

    # 等待 1 秒讓各個子程序有時間啟動及輸出錯誤訊息
    time.sleep(1)

    success = True
    for script, proc in processes:
        if proc.poll() is None:
            print(f"✅ {script} 載入成功")
        else:
            print(f"❌ {script} 載入失敗")
            success = False

    print("\n錯誤報告:")
    for script in scripts:
        if script in error_logs and error_logs[script]:
            print(f"---- {script} 的錯誤:")
            for err_line in error_logs[script]:
                print(err_line)
        else:
            print(f"---- {script} 無錯誤訊息。")

    if not success:
        print("\n❌ 測試醬 無法登入.")
        sys.exit(1)
    else:
        print("\n✅ 測試醬 已登入.")

    # 主程序持續運行，避免 main.py 執行完畢後退出
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down all subprocesses...")
        for script, proc in processes:
            proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
