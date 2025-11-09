# Lost & Found Platform

An intelligent campus lost and found platform built with FastAPI, Vue.js, and PostgreSQL.

## Features

### Core Features
- **User Authentication**: Email/password registration and login with JWT tokens
- **User Management**: Profile management, notifications, and credit scoring system
- **Community Forum**: Create posts, comment on posts, and engage with the community
- **Real-time Notifications**: Get notified about comments and other activities
- **Responsive Design**: Modern, mobile-friendly UI built with Tailwind CSS

### Lost & Found Features ✨
- **Item Categories**: Organize lost and found items by category (electronics, documents, keys, etc.)
- **Smart Matching**: Intelligent recommendation system to match lost and found items
- **Image Upload**: Support multiple image uploads for item posts
- **Advanced Search**: Filter by category, location, time, and claimed status
- **Claim System**: Complete claim workflow with approval/rejection
- **Rating System**: Mutual rating between item owners and claimers
- **Credit Score**: Automatic credit score updates based on ratings
- **Detailed Information**: Track item location, time, and contact information

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: Type-safe ORM that combines SQLAlchemy and Pydantic
- **PostgreSQL**: Robust, open-source relational database
- **JWT**: Secure authentication with JSON Web Tokens
- **Alembic**: Database migration tool

### Frontend
- **Vue 3**: Progressive JavaScript framework with Composition API
- **Pinia**: State management for Vue applications
- **Vue Router**: Official router for Vue.js
- **Axios**: HTTP client for API communication
- **Tailwind CSS**: Utility-first CSS framework

## Project Structure

```
lost-and-found-platform/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality (security, config)
│   │   ├── models/        # SQLModel database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── database.py    # Database configuration
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── start.py          # Startup script
├── frontend/
│   └── frontend/
│       ├── src/
│       │   ├── api/       # API client configuration
│       │   ├── components/ # Vue components
│       │   ├── stores/    # Pinia stores
│       │   ├── views/     # Vue pages
│       │   └── router/    # Vue Router configuration
│       └── package.json   # Node.js dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Start the backend server:
   ```bash
   python start.py
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/notifications` - Get user notifications
- `PUT /api/users/notifications/{id}/read` - Mark notification as read

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}` - Get category detail

### Posts (Lost & Found)
- `GET /api/posts` - List posts (with filtering)
- `POST /api/posts` - Create post
- `GET /api/posts/{id}` - Get post detail
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post
- `GET /api/posts/{id}/matches` - Get smart matches for a post
- `GET /api/posts/search/advanced` - Advanced search
- `POST /api/posts/{id}/comments` - Add comment
- `GET /api/posts/{id}/comments` - List comments
- `DELETE /api/posts/comments/{id}` - Delete comment

### Claims ✨
- `POST /api/claims/` - Create claim request
- `GET /api/claims/my-claims` - Get my claim requests
- `GET /api/claims/post/{id}` - Get claims for a post
- `POST /api/claims/{id}/approve` - Approve a claim
- `POST /api/claims/{id}/reject` - Reject a claim
- `DELETE /api/claims/{id}` - Cancel a claim

### Ratings ✨
- `POST /api/ratings/` - Create rating
- `GET /api/ratings/claim/{id}` - Get ratings for a claim
- `GET /api/ratings/user/{id}/received` - Get ratings received by user

### Users ✨
- `GET /api/users/{id}` - Get user public information
- `GET /api/users/{id}/posts` - Get user's posts
- `GET /api/users/{id}/ratings` - Get user's ratings

### Upload
- `POST /api/upload/upload` - Upload single image
- `POST /api/upload/upload-multiple` - Upload multiple images
- `DELETE /api/upload/{filename}` - Delete image

## Database Schema

The application uses the following main entities:

- **Users**: User accounts with authentication, profile information, and credit scores
- **Categories**: Item categories (electronics, documents, keys, books, etc.)
- **Posts**: Forum posts with lost/found item information
- **Comments**: Comments on posts
- **Notifications**: System notifications for users
- **Claims** ✨: Claim requests for lost and found items
- **Ratings** ✨: User ratings after successful claims

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend/frontend
npm run test
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Documentation

- **[Claim System Complete Guide](./CLAIM_SYSTEM_COMPLETE.md)** - Complete implementation report of the claim system
- **[User Profile Feature](./USER_PROFILE_COMPLETE.md)** - User profile and rating display feature
- **[Testing Checklist](./TESTING_CHECKLIST.md)** - Comprehensive testing guide
- **[Development Summary](./DEVELOPMENT_SUMMARY.md)** - Development completion summary

## Current Status

### Completed Features (≈ 90%)
- ✅ User authentication and authorization
- ✅ User profile management
- ✅ Forum system with posts and comments
- ✅ Notification system
- ✅ Item categories
- ✅ Image upload (single and multiple)
- ✅ Advanced search and filtering
- ✅ Smart matching algorithm
- ✅ **Claim system** (NEW)
- ✅ **Rating system** (NEW)
- ✅ **Credit score system** (NEW)
- ✅ **User profile page** (NEW) ✨

### Optional Enhancements
- ⚠️ Admin dashboard
- ⚠️ Real-time messaging
- ⚠️ Email notifications
- ⚠️ Data analytics and reports

## License

This project is licensed under the MIT License.

