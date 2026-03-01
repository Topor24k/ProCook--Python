# ProCook - Recipe Manager

A full-stack recipe management application with a **Python/Flask** backend, **PostgreSQL** database, and a **React** frontend.

## Tech Stack

### Backend
- **Python 3.10+** with **Flask**
- **PostgreSQL** database
- **Flask-SQLAlchemy** ORM
- **Flask-Login** session authentication
- **Flask-Migrate** for database migrations

### Frontend
- **React 18** with React Router
- **Vite** build tool
- **Tailwind CSS** for styling
- **Axios** for API calls

## Features

- User registration & login (session-based authentication)
- Create, read, update, delete recipes with ingredients
- Image upload for recipes
- Comment system with nested replies
- 5-star rating system
- Save/bookmark recipes
- User profile with statistics
- Account deletion with data retention options

## Project Structure

```
├── backend/                # Python Flask backend
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration
│   ├── models.py           # SQLAlchemy models
│   └── routes/             # API route blueprints
│       ├── auth.py         # Authentication routes
│       ├── recipes.py      # Recipe CRUD routes
│       ├── comments.py     # Comment routes
│       ├── ratings.py      # Rating routes
│       └── saved_recipes.py# Saved recipes routes
├── resources/              # Frontend source
│   ├── js/                 # React components & pages
│   └── css/                # Stylesheets
├── run.py                  # Flask entry point
├── seed.py                 # Database seeder
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── vite.config.js          # Vite configuration
└── index.html              # SPA entry point
```

## Quick Start

See [HOW_TO_RUN.md](HOW_TO_RUN.md) for detailed setup instructions.
