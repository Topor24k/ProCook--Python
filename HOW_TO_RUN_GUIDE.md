# ProCook Python - How to Run Guide

## Prerequisites

Before running the application, ensure you have:

- ✅ Python 3.8+ installed
- ✅ Node.js 16+ installed
- ✅ PostgreSQL 14+ installed and running
- ✅ Database `procook` created in pgAdmin4
- ✅ Environment variables configured in `.env` file

---

## Quick Start (3 Steps)

### Step 1: Start PostgreSQL
Make sure PostgreSQL is running on port **5432**. Check in pgAdmin4 or Services.

### Step 2: Start Backend Server
Open **Terminal 1** (PowerShell):

```powershell
# Navigate to project directory
cd "C:\Users\Kayeen Campana\ProCook - Python"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Flask backend
python run.py
```

✅ **Backend running at**: http://localhost:5000

### Step 3: Start Frontend Server
Open **Terminal 2** (PowerShell):

```powershell
# Navigate to project directory
cd "C:\Users\Kayeen Campana\ProCook - Python"

# Start Vite development server
npm run dev
```

✅ **Frontend running at**: http://localhost:5173

---

## Detailed Instructions

### 1️⃣ Database Setup (One-time)

#### Check PostgreSQL Status
```powershell
# Check if PostgreSQL is running
Get-Service -Name postgresql*
```

If not running, start it:
```powershell
Start-Service postgresql-x64-14
```

#### Verify Database Exists
Open **pgAdmin4** and check:
- Server: `localhost:5432`
- Database: `procook`
- User: `postgres`
- Password: `Topor24kKayeen`

#### Create Tables (if not already created)
```powershell
# Connect to database and run schema
psql -U postgres -d procook -f create_tables.sql
```

Or execute SQL from pgAdmin4 Query Tool.

---

### 2️⃣ Environment Configuration

Verify `.env` file exists in project root:

```env
DATABASE_URL=postgresql://postgres:Topor24kKayeen@localhost:5432/procook
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:5000
```

---

### 3️⃣ Backend Server

#### Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt
```

#### Install Dependencies (First time only)
```powershell
pip install -r requirements.txt
```

#### Start Flask Server
```powershell
python run.py
```

**Expected Output:**
```
 * Serving Flask app 'backend.app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

#### Test Backend API
Open browser or PowerShell:
```powershell
# Test health endpoint
Invoke-RestMethod -Uri http://localhost:5000/api/user -Method GET
```

---

### 4️⃣ Frontend Server

#### Open New Terminal
Keep backend terminal running. Open **new PowerShell terminal**.

#### Install Node Modules (First time only)
```powershell
npm install
```

#### Start Vite Dev Server
```powershell
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

### 5️⃣ Access Application

Open your web browser:

🌐 **http://localhost:5173**

You should see the ProCook homepage!

---

## Running Both Servers (Full Workflow)

### Option 1: Using Two Terminals

**Terminal 1 - Backend:**
```powershell
cd "C:\Users\Kayeen Campana\ProCook - Python"
.\venv\Scripts\Activate.ps1
python run.py
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\Users\Kayeen Campana\ProCook - Python"
npm run dev
```

### Option 2: Using VS Code Integrated Terminal

1. Press **Ctrl + `** to open terminal
2. Click **+** icon to create split terminals
3. Run backend in first terminal
4. Run frontend in second terminal

---

## Stopping the Application

### Stop Backend
In backend terminal, press **Ctrl + C**

### Stop Frontend
In frontend terminal, press **Ctrl + C**

### Stop PostgreSQL (if needed)
```powershell
Stop-Service postgresql-x64-14
```

---

## Common Commands

### Backend Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Run Flask shell
python -c "from backend.app import create_app, db; app = create_app(); app.app_context().push()"

# Run database seed
python seed.py
```

### Frontend Commands

```powershell
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Add new package
npm install package-name
```

### Database Commands

```powershell
# Connect to PostgreSQL
psql -U postgres -d procook

# List all tables
\dt

# Describe table structure
\d table_name

# Run SQL file
psql -U postgres -d procook -f filename.sql

# Backup database
pg_dump -U postgres procook > backup.sql

# Restore database
psql -U postgres procook < backup.sql
```

---

## Troubleshooting

### ❌ Problem: "Port 5000 is already in use"

**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### ❌ Problem: "Port 5173 is already in use"

**Solution:**
```powershell
# Find and kill process on port 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### ❌ Problem: "Cannot activate virtual environment"

**Solution:**
```powershell
# Set execution policy (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

### ❌ Problem: "Database connection error"

**Check:**
1. PostgreSQL is running: `Get-Service postgresql*`
2. Database exists in pgAdmin4
3. `.env` file has correct DATABASE_URL
4. Firewall allows port 5432

**Solution:**
```powershell
# Restart PostgreSQL
Restart-Service postgresql-x64-14

# Test connection
psql -U postgres -d procook -c "SELECT version();"
```

### ❌ Problem: "Module not found" (Python)

**Solution:**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### ❌ Problem: "Module not found" (Node.js)

**Solution:**
```powershell
# Delete node_modules and package-lock.json
Remove-Item -Recurse -Force node_modules, package-lock.json

# Reinstall
npm install
```

### ❌ Problem: "CORS errors in browser console"

**Check:**
- Backend is running on port 5000
- Frontend is running on port 5173
- `.env` has correct CORS_ORIGINS
- Browser is accessing http://localhost:5173 (not 127.0.0.1)

---

## Development Workflow

### Daily Development

1. **Start PostgreSQL** (if not auto-starting)
2. **Start Backend** (Terminal 1)
3. **Start Frontend** (Terminal 2)
4. **Code changes** auto-reload in both servers
5. **Stop servers** when done (Ctrl + C)

### Making Changes

**Backend Changes** (Python files):
- Flask auto-reloads on file save
- No need to restart server

**Frontend Changes** (React files):
- Vite HMR (Hot Module Replacement) updates instantly
- No need to restart server

**Database Schema Changes**:
- Modify `backend/models.py`
- Run migrations or recreate tables
- Restart backend server

---

## Project Structure

```
ProCook - Python/
│
├── backend/              # Python Flask backend
│   ├── app.py           # Flask app factory
│   ├── models.py        # Database models
│   ├── routes/          # API endpoints
│   └── config.py        # Configuration
│
├── resources/           # Frontend source code
│   ├── js/              # React components
│   └── css/             # Stylesheets
│
├── public/              # Static assets (images)
├── uploads/             # User uploaded files
│
├── venv/                # Python virtual environment
├── node_modules/        # Node.js dependencies
│
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies
│
├── run.py               # Backend entry point
├── vite.config.js       # Vite configuration
└── index.html           # Frontend entry point
```

---

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `PUT /api/profile/password` - Change password

### Recipes
- `GET /api/recipes` - List all recipes
- `GET /api/recipes/:id` - Get recipe details
- `POST /api/recipes` - Create recipe (auth required)
- `PUT /api/recipes/:id` - Update recipe (auth required)
- `DELETE /api/recipes/:id` - Delete recipe (auth required)
- `GET /api/my-recipes` - Get user's recipes (auth required)

### Comments
- `GET /api/recipes/:id/comments` - List comments
- `POST /api/recipes/:id/comments` - Create comment (auth required)
- `PUT /api/recipes/:id/comments/:comment_id` - Update comment (auth required)
- `DELETE /api/recipes/:id/comments/:comment_id` - Delete comment (auth required)

### Ratings
- `POST /api/recipes/:id/rating` - Rate recipe (auth required)
- `GET /api/recipes/:id/rating` - Get user rating (auth required)
- `GET /api/recipes/:id/rating/public` - Get average rating
- `DELETE /api/recipes/:id/rating` - Delete rating (auth required)

### Saved Recipes
- `GET /api/saved-recipes` - List saved recipes (auth required)
- `GET /api/recipes/:id/saved` - Check if saved (auth required)
- `POST /api/recipes/:id/save` - Toggle save (auth required)

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `FLASK_APP` | Flask application entry point | `run.py` |
| `FLASK_ENV` | Flask environment mode | `development` or `production` |
| `SECRET_KEY` | Flask session secret key | Random string |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |

---

## Production Deployment

### Build Frontend
```powershell
npm run build
```
This creates `dist/` folder with optimized static files.

### Run Backend in Production
```powershell
# Use production WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app()"
```

### Serve Static Files
Configure Nginx or Apache to serve `dist/` folder and proxy API requests to Flask backend.

---

## Need Help?

- Check the [OOP_AND_CRUD_DOCUMENTATION.md](OOP_AND_CRUD_DOCUMENTATION.md) for code details
- Review error messages in terminal output
- Check browser console for frontend errors (F12)
- Verify PostgreSQL logs in pgAdmin4

---

**Last Updated**: March 5, 2026  
**Project**: ProCook - Python Recipe Manager  
**Tech Stack**: Flask + React + PostgreSQL
