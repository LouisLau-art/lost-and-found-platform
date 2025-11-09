"""
创建admin@example.com管理员用户
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
from app.core.security import get_password_hash

def create_admin():
    """创建admin@example.com管理员用户"""
    print("正在创建admin用户...")
    
    with Session(engine) as session:
        # 检查用户是否已存在
        existing = session.exec(
            select(User).where(User.email == "admin@example.com")
        ).first()
        
        if existing:
            print(f"用户已存在: {existing.email}")
            print(f"  姓名: {existing.name}")
            print(f"  is_admin: {existing.is_admin}")
            
            if not existing.is_admin:
                existing.is_admin = True
                session.add(existing)
                session.commit()
                print("✓ 已将用户设置为管理员")
            else:
                print("✓ 用户已经是管理员")
            return
        
        # 创建新用户
        admin = User(
            name="管理员",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            credit_score=100,
            is_admin=True
        )
        
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"✅ 成功创建admin用户")
        print(f"  邮箱: {admin.email}")
        print(f"  密码: admin123")
        print(f"  姓名: {admin.name}")
        print(f"  is_admin: {admin.is_admin}")

if __name__ == "__main__":
    try:
        create_admin()
    except Exception as e:
        print(f"❌ 发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
