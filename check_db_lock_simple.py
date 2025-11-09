import os
import subprocess

db_path = r'c:\Users\Louis\Desktop\lost-and-found-platform\backend\lostandfound.db'
print(f"正在检查数据库文件: {db_path}")

# 尝试简单的文件操作测试锁定
print("\n测试文件锁定状态:")
try:
    with open(db_path, 'a') as f:
        print("文件可写入，可能未被完全锁定。")
except IOError as e:
    print(f"文件锁定错误: {e}")

# 列出所有Python进程
print("\n所有Python进程:")
try:
    result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"获取进程列表失败: {e}")

# 尝试直接删除数据库文件（作为最后的手段）
print("\n尝试重命名数据库文件以释放锁定:")
try:
    backup_path = db_path + '.old'
    if os.path.exists(backup_path):
        os.remove(backup_path)
    os.rename(db_path, backup_path)
    print(f"成功将数据库文件重命名为: {backup_path}")
except Exception as e:
    print(f"重命名失败: {e}")