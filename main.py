import subprocess
import signal
import sys

def main():
    try:
        # 啟動 chat.py
        process_chat = subprocess.Popen(["python", "chat.py"])
        # 啟動 boss.py
        process_boss = subprocess.Popen(["python", "boss.py"])
        # 啟動 food.py
        process_food = subprocess.Popen(["python", "food.py"])
        # 啟動 material.py
        process_material = subprocess.Popen(["python", "material.py"])

        # 等待兩個進程都結束
        process_chat.wait()
        process_boss.wait()
        process_food.wait()
        process_material.wait()
    except KeyboardInterrupt:
        print("收到中斷訊號，正在終止程序...")
        # 終止進程
        process_chat.send_signal(signal.SIGINT)
        process_boss.send_signal(signal.SIGINT)
        process_food.send_signal(signal.SIGINT)
        process_material.send_signal(signal.SIGINT)
        
        # 如果需要強制結束，使用 terminate() 或 kill()
        process_chat.terminate()
        process_boss.terminate()
        process_food.terminate()
        process_material.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
