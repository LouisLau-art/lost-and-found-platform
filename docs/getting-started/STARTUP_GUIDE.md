# Lost and Found Platform Startup Guide

## New Startup Script Usage

I've created an enhanced startup script `start-project.bat` with the following features:

### Features

1. **Menu Selection** - Choose to start the full platform, backend only, or frontend only
2. **Environment Check** - Automatically detects Python, Node.js, and project dependencies
3. **Auto Repair** - Attempts to create missing virtual environments and install dependencies
4. **User-Friendly** - Provides clear startup information and prompts

### How to Use

1. **Run the script directly**:
   - Double-click `start-project.bat` in File Explorer
   - Or run in Command Prompt: `start-project.bat`

2. **Select an option**:
   - Enter `1` - Start full platform (frontend and backend)
   - Enter `2` - Start backend service only
   - Enter `3` - Start frontend service only
   - Enter `4` - Check environment configuration
   - Enter `0` - Exit script

## Service Access URLs

- **Backend Service**: http://localhost:8000
- **Frontend Service**: http://localhost:5173

## First Run Notes

1. **Environment Requirements**:
   - Python (3.8+ recommended)
   - Node.js and npm

2. **First startup may take time**:
   - If virtual environment doesn't exist, the script will create it and install dependencies
   - If frontend dependencies are not installed, the script will automatically run `npm install`

3. **Service Status**:
   - Please wait for services to fully start before accessing
   - Backend success message: "Uvicorn running on http://localhost:8000"
   - Frontend success message: "Local: http://localhost:5173/"

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   - If ports 8000 or 5173 are already in use, close the conflicting applications and try again

2. **Dependency Installation Failures**:
   - Ensure network connection is stable
   - Try manually creating virtual environment and installing dependencies

3. **Database Errors**:
   - If you encounter database-related errors, try running `backend\init_db.py` to initialize the database

## Original Startup Scripts

The following original startup scripts are still available:

- `start-all.bat` - Start full platform
- `start-backend.bat` - Start backend service only
- `start-frontend.bat` - Start frontend service only

You can choose to use whichever startup script suits your needs.

---

Enjoy using the platform! If you have any questions, please refer to the relevant project documentation.