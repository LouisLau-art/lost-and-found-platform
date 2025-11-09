"""
设置Louis用户为管理员的脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User

def set_louis_admin():
    """将Louis用户设置为管理员"""
    print("正在连接数据库...")
    
    with Session(engine) as session:
        # 查找Louis用户（通过name或email）
        statement = select(User).where(
            (User.name.like("%Louis%")) | (User.email.like("%louis%"))
        )
        users = session.exec(statement).all()
        
        if not users:
            print("❌ 未找到名为Louis的用户")
            print("\n所有用户列表：")
            all_users = session.exec(select(User)).all()
            for user in all_users:
                admin_status = "✓ 管理员" if user.is_admin else "✗ 普通用户"
                print(f"  - {user.name} ({user.email}) [{admin_status}]")
            return
        
        print(f"\n找到 {len(users)} 个匹配的用户：")
        for idx, user in enumerate(users, 1):
            admin_status = "已是管理员" if user.is_admin else "普通用户"
            print(f"{idx}. {user.name} ({user.email}) - {admin_status}")
        
        # 设置所有匹配用户为管理员
        updated_count = 0
        for user in users:
            if not user.is_admin:
                user.is_admin = True
                session.add(user)
                updated_count += 1
                print(f"\n✓ 已将用户 {user.name} ({user.email}) 设置为管理员")
            else:
                print(f"\n- 用户 {user.name} ({user.email}) 已经是管理员，跳过")
        
        if updated_count > 0:
            session.commit()
            print(f"\n✅ 成功更新 {updated_count} 个用户的管理员权限")
        else:
            print("\n✅ 无需更新，所有匹配用户已经是管理员")

if __name__ == "__main__":
    print("=" * 60)
    print("设置Louis为管理员")
    print("=" * 60)
    try:
        set_louis_admin()
    except Exception as e:
        print(f"\n❌ 发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
    print("=" * 60)
