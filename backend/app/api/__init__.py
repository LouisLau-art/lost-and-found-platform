from fastapi import APIRouter

# Import subrouters
from . import auth, users, categories, posts, upload, claims, ratings, notifications
from .admin import posts as admin_posts

# Aggregate API router
router = APIRouter()

# Public/auth routes
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])

# Domain routes
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(posts.router, prefix="/posts", tags=["Posts"])
router.include_router(upload.router, prefix="/upload", tags=["Upload"])
router.include_router(claims.router, prefix="/claims", tags=["Claims"])
router.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Admin routes
router.include_router(admin_posts.router, prefix="/admin", tags=["Admin"])
