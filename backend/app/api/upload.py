from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from typing import List
import os
import uuid
from pathlib import Path
from app.core.deps import get_current_user, get_current_admin_user
from app.database import get_session
from app.models.user import User

router = APIRouter()

# 配置上传目录
UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的图片格式
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(file: UploadFile) -> None:
    """验证图片文件"""
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传单张图片"""
    validate_image(file)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 读取文件内容并检查大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 返回文件URL（相对路径）
    file_url = f"/uploads/images/{unique_filename}"
    return {
        "filename": unique_filename,
        "url": file_url,
        "message": "Image uploaded successfully"
    }

@router.post("/upload-multiple", response_model=dict)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传多张图片"""
    if len(files) > 9:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 9 images allowed"
        )
    
    uploaded_files = []
    
    for file in files:
        validate_image(file)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # 读取文件内容并检查大小
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds maximum allowed size"
            )
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 添加到已上传列表
        file_url = f"/uploads/images/{unique_filename}"
        uploaded_files.append({
            "filename": unique_filename,
            "url": file_url
        })
    
    return {
        "files": uploaded_files,
        "count": len(uploaded_files),
        "message": f"{len(uploaded_files)} images uploaded successfully"
    }

@router.delete("/{filename}")
async def delete_image(
    filename: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """删除图片（仅允许图片所有者或管理员删除）"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # 权限检查：仅允许管理员或图片所有者删除
    # 由于没有图片所有者信息，这里简化为只允许管理员删除
    if not getattr(current_user, 'is_admin', False):
        # 如果不是管理员，需要检查是否为图片所有者
        # 注：这里需要从数据库中查询图片的所有者
        # 为简化实现，目前仅允许管理员删除
        from app.models.post import Post
        from sqlmodel import select
        
        # 查找使用此图片的帖子
        image_url = f"/uploads/images/{filename}"
        statement = select(Post).where(Post.images.contains(image_url))  # type: ignore
        posts = session.exec(statement).all()
        
        # 检查是否有任何帖子属于当前用户
        is_owner = any(post.author_id == current_user.id for post in posts)
        
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限删除此图片，只有图片所有者或管理员可以删除"
            )
    
    os.remove(file_path)
    
    return {"message": "Image deleted successfully"}
