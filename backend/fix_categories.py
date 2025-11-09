from sqlmodel import Session, select
from app.database import engine
from app.models.category import Category

# Category name mappings
category_translations = {
    '电子设备': 'Electronics',
    '证件卡片': 'Documents',
    '服饰配饰': 'Clothing & Accessories',
    '书包文具': 'Stationery',
    '生活用品': 'Daily Items',
    '运动器材': 'Sports Equipment',
    '其他物品': 'Others'
}

session = Session(engine)
cats = session.exec(select(Category)).all()
print(f'Updating {len(cats)} categories...')

for cat in cats:
    if cat.name_en is None and cat.name in category_translations:
        cat.name_en = category_translations[cat.name]
        print(f'Updated {cat.name} -> {cat.name_en}')

session.commit()
print('Done!')
