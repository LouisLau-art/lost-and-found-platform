from sqlmodel import Session, create_engine, select
from app.models.user import User
from app.core.security import get_password_hash
import os

# 数据库连接配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lostandfound.db")
engine = create_engine(DATABASE_URL)

# 重置Test User A的密码
with Session(engine) as session:
    # 查询Test User A
    user = session.exec(select(User).where(User.email == "testuserA@example.com")).first()
    if not user:
        print("Test User A不存在")
        exit(1)
    
    # 设置新密码为testpassword
    new_password = "testpassword"
    user.password_hash = get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    print(f"Test User A密码已重置为{new_password}")
