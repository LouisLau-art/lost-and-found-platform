from sqlmodel import Session, select
from app.database import engine
from app.models.user import User

session = Session(engine)
users = session.exec(select(User)).all()
print(f'Total users: {len(users)}')
for u in users:
    print(f'ID: {u.id}, name: {u.name}, email: {u.email}')
    print(f'  has is_admin attr: {hasattr(u, "is_admin")}')
    if hasattr(u, 'is_admin'):
        print(f'  is_admin: {u.is_admin} (type: {type(u.is_admin).__name__})')
    print()
