# 💰 Expense Tracker System

A full-stack Expense Tracker application built with **FastAPI**, **SQLAlchemy**, and a premium **Vanilla JS** frontend featuring dynamic data visualization.

## ✨ Features

- **User Authentication** — Secure JWT-based login & registration
- **Expense Management** — Full CRUD operations for tracking expenses
- **Category Management** — Custom categories with inline add/edit/delete
- **Interactive Dashboard** — Real-time charts and analytics powered by Chart.js
- **Responsive Design** — Premium glassmorphism UI that works across all devices

## 🛠️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | FastAPI, SQLAlchemy, Alembic      |
| Frontend   | HTML, CSS, Vanilla JavaScript     |
| Database   | SQLite (dev) / PostgreSQL (prod)  |
| Auth       | JWT (JSON Web Tokens)             |
| Charts     | Chart.js                          |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/dhanesh-vaishnav96/Expense_Tracker_System.git
cd Expense_Tracker_System

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn backend.main:app --reload
```

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./expense_tracker.db
```

## 📁 Project Structure

```
Expense Tracker/
├── backend/
│   ├── config/         # Database configuration
│   ├── models/         # SQLAlchemy models
│   ├── routes/         # API endpoints
│   ├── schemas/        # Pydantic schemas
│   └── main.py         # Application entry point
├── frontend/
│   ├── static/         # CSS & JavaScript
│   └── templates/      # HTML templates
├── alembic/            # Database migrations
├── requirements.txt
└── README.md
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👤 Author

**Dhanesh Vaishnav**
- GitHub: [@dhanesh-vaishnav96](https://github.com/dhanesh-vaishnav96)
- Email: dhaneshvaishnav123@gmail.com
