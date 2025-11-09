from sqlmodel import Session, select
from app.database import engine
from app.models.user import User

with Session(engine) as session:
    users = session.exec(select(User).order_by(User.id).limit(20)).all()
    for user in users:
        print(f"ID: {user.id}, email: {user.email}, name: {user.name}, admin: {user.is_admin}")
