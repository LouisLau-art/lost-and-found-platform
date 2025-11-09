from sqlmodel import Session, select
from app.database import engine
from app.models.category import Category

session = Session(engine)
cats = session.exec(select(Category)).all()
print(f'Total categories: {len(cats)}')
for c in cats:
    print(f'ID: {c.id}')
    print(f'  name: {c.name!r} (type: {type(c.name).__name__})')
    print(f'  name_en: {c.name_en!r} (type: {type(c.name_en).__name__})')
    print(f'  description: {c.description!r}')
    print(f'  icon: {c.icon!r}')
    print(f'  is_active: {c.is_active}')
    print(f'  created_at: {c.created_at}')
    print()
