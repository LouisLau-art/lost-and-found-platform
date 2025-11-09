from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryRead])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    show_all: bool = False,  # 是否显示已禁用的分类
    session: Session = Depends(get_session)
):
    """获取所有物品分类"""
    statement = select(Category)
    
    if not show_all:
        statement = statement.where(Category.is_active == True)
    
    statement = statement.offset(skip).limit(limit).order_by(Category.id)
    categories = session.exec(statement).all()
    
    # Convert to response model explicitly to avoid relationship loading issues
    return [CategoryRead.model_validate(cat) for cat in categories]

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    session: Session = Depends(get_session)
):
    """获取单个分类详情"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.post("/", response_model=CategoryRead)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),  # 使用管理员权限检查
    session: Session = Depends(get_session)
):
    """创建新分类（需要管理员权限）"""
    
    # 检查分类名称是否已存在
    statement = select(Category).where(Category.name == category.name)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    
    db_category = Category(**category.model_dump())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_admin_user),  # 使用管理员权限检查
    session: Session = Depends(get_session)
):
    """更新分类信息（需要管理员权限）"""
    
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 更新字段
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_admin_user),  # 使用管理员权限检查
    session: Session = Depends(get_session)
):
    """删除分类（软删除，设置为不活跃）"""
    
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.is_active = False
    session.add(category)
    session.commit()

    return {"message": "Category deleted successfully"}
