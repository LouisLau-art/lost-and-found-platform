"""
初始化物品分类数据
在数据库中创建预设的物品分类
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models.category import Category

# 预设分类数据
CATEGORIES = [
    {
        "name": "电子产品",
        "name_en": "electronics",
        "description": "手机、平板、笔记本电脑、耳机、充电器等",
        "icon": "📱"
    },
    {
        "name": "证件卡类",
        "name_en": "documents",
        "description": "学生证、身份证、银行卡、公交卡等",
        "icon": "🪪"
    },
    {
        "name": "钥匙",
        "name_en": "keys",
        "description": "宿舍钥匙、车钥匙、钥匙扣等",
        "icon": "🔑"
    },
    {
        "name": "书籍文具",
        "name_en": "books_stationery",
        "description": "教材、笔记本、文具用品等",
        "icon": "📚"
    },
    {
        "name": "衣物配饰",
        "name_en": "clothing_accessories",
        "description": "外套、围巾、帽子、手套、眼镜等",
        "icon": "👔"
    },
    {
        "name": "包袋箱类",
        "name_en": "bags",
        "description": "背包、手提包、钱包、行李箱等",
        "icon": "🎒"
    },
    {
        "name": "运动器材",
        "name_en": "sports_equipment",
        "description": "篮球、羽毛球拍、运动鞋等",
        "icon": "⚽"
    },
    {
        "name": "生活用品",
        "name_en": "daily_items",
        "description": "雨伞、水杯、化妆品等",
        "icon": "☂️"
    },
    {
        "name": "宠物",
        "name_en": "pets",
        "description": "走失或拾到的宠物",
        "icon": "🐾"
    },
    {
        "name": "其他",
        "name_en": "others",
        "description": "其他未分类物品",
        "icon": "📦"
    }
]

def init_categories():
    """初始化分类数据"""
    print("正在初始化物品分类...")
    
    with Session(engine) as session:
        # 检查是否已有分类数据
        statement = select(Category)
        existing_categories = session.exec(statement).all()
        
        if existing_categories:
            print(f"已存在 {len(existing_categories)} 个分类，跳过初始化")
            return
        
        # 添加分类
        for cat_data in CATEGORIES:
            category = Category(**cat_data)
            session.add(category)
            print(f"添加分类: {cat_data['name']} ({cat_data['name_en']})")
        
        session.commit()
        print(f"成功创建 {len(CATEGORIES)} 个分类！")

if __name__ == "__main__":
    try:
        init_categories()
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
