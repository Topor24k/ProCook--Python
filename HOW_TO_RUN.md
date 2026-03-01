# ProCook Recipe Manager — How to Run

## Prerequisites

Make sure you have the following installed:

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **npm** (comes with Node.js)

---

## 1. Clone & Navigate

```bash
cd "ProCook - Python"
```

## 2. Create the PostgreSQL Database

Open a terminal / psql and run:

```sql
CREATE DATABASE procook;
```

Or using the command line:

```bash
createdb procook
```

## 3. Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/procook
CORS_ORIGINS=http://localhost:5173,http://localhost:8000
```

## 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 5. Create Database Tables & Seed Data

```bash
python seed.py
```

This will:
- Create all database tables
- Insert sample data (demo user + sample recipes)
- Demo account: `demo@procook.com` / `Password123`

## 6. Install Frontend Dependencies

```bash
npm install
```

## 7. Run the Application

You need **two terminals**:

### Terminal 1 — Python Backend (port 8000)

```bash
python run.py
```

### Terminal 2 — Vite Frontend Dev Server (port 5173)

```bash
npm run dev
```

## 8. Open in Browser

Visit: **http://localhost:5173**

---

## Production Build

To build the frontend for production:

```bash
npm run build
```

Then run only the Flask server — it will serve the built frontend from the `dist/` directory:

```bash
python run.py
```

Visit: **http://localhost:8000**

---

## API Endpoints

### Public Routes
| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| GET    | `/api/recipes`                    | List all recipes         |
| GET    | `/api/recipes/:id`                | Get recipe details       |
| GET    | `/api/recipes/:id/rating/public`  | Get public rating        |
| GET    | `/api/recipes/:id/comments`       | Get recipe comments      |

### Auth Routes
| Method | Endpoint           | Description         |
|--------|--------------------|---------------------|
| POST   | `/api/register`    | Register new user   |
| POST   | `/api/login`       | Login               |
| POST   | `/api/logout`      | Logout              |

### Protected Routes (requires login)
| Method | Endpoint                              | Description              |
|--------|---------------------------------------|--------------------------|
| GET    | `/api/user`                           | Get current user         |
| GET    | `/api/profile`                        | Get profile with stats   |
| PUT    | `/api/profile`                        | Update profile           |
| PUT    | `/api/profile/password`               | Change password          |
| DELETE | `/api/profile`                        | Delete account           |
| POST   | `/api/recipes`                        | Create recipe            |
| PUT    | `/api/recipes/:id`                    | Update recipe            |
| DELETE | `/api/recipes/:id`                    | Delete recipe            |
| GET    | `/api/recipes/my-recipes`             | Get user's recipes       |
| POST   | `/api/recipes/:id/comments`           | Add comment              |
| PUT    | `/api/recipes/:id/comments/:cid`      | Update comment           |
| DELETE | `/api/recipes/:id/comments/:cid`      | Delete comment           |
| GET    | `/api/recipes/:id/rating`             | Get user's rating        |
| POST   | `/api/recipes/:id/rating`             | Submit rating            |
| DELETE | `/api/recipes/:id/rating`             | Delete rating            |
| GET    | `/api/saved-recipes`                  | List saved recipes       |
| GET    | `/api/recipes/:id/saved`              | Check if saved           |
| POST   | `/api/recipes/:id/save`               | Toggle save/unsave       |

---

## Troubleshooting

- **Database connection error**: Make sure PostgreSQL is running and the `DATABASE_URL` in `.env` is correct.
- **Port conflict**: If port 8000 or 5173 is in use, update `run.py` or `vite.config.js` accordingly.
- **Module not found**: Run `pip install -r requirements.txt` again.
- **Frontend not loading**: Make sure `npm install` was run and the Vite dev server is running.
