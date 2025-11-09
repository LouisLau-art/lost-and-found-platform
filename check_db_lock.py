import psutil
import os

db_path = r'c:\Users\Louis\Desktop\lost-and-found-platform\backend\lostandfound.db'
print(f"正在检查占用数据库文件的进程: {db_path}")
print("\n正在使用该文件的进程:")
found = False

for proc in psutil.process_iter(['pid', 'name', 'exe']):
    try:
        # 获取进程打开的文件
        files = proc.open_files()
        for file_info in files:
            if file_info.path.lower() == db_path.lower():
                print(f"PID: {proc.pid}, 进程名: {proc.name()}, 可执行文件: {proc.exe()}")
                found = True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if not found:
    print("没有找到直接占用该数据库文件的进程。")

# 检查是否有Python进程可能在后台运行
print("\n所有正在运行的Python进程:")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.name().lower():
            cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A'
            print(f"PID: {proc.pid}, 命令行: {cmdline}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass